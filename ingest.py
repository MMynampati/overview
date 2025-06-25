# ingest.py
import logging
import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

# Import our new custom modules
from core.crawler import get_category_links, get_article_links_from_category, scrape_article_content
from core.loader import WebContentLoader

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
BASE_URL = "https://docs.overview.ai/docs/user-manual"
PRODUCT_LANDING_PAGE_URL = "https://docs.overview.ai/docs/start-here"
DB_PATH = os.getenv('DB_PATH', 'vectorstore')
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

def crawl_documentation():
    """
    Crawl the documentation site using the new Document360-specific crawler.
    Returns a list of LangChain Document objects.
    """
    logger.info("--- Starting Documentation Crawl ---")
    
    all_articles_data = []
    categories = get_category_links(PRODUCT_LANDING_PAGE_URL)
    
    if not categories:
        logger.error("No categories found. Check the selectors in crawler.py")
        return []
    
    for category in categories:
        articles_to_scrape = get_article_links_from_category(category['url'], category['name'])
        
        for article_info in articles_to_scrape:
            scraped_data = scrape_article_content(article_info)
            if scraped_data:
                all_articles_data.append(scraped_data)
    
    logger.info(f"Crawled {len(all_articles_data)} articles from {len(categories)} categories")
    
    # Convert to LangChain Documents
    documents = []
    for article in all_articles_data:
        doc = Document(
            page_content=article['content'],
            metadata={
                'source': article['source'],
                'title': article['title'],
                'category': article['category']
            }
        )
        documents.append(doc)
    
    return documents

def main():
    """
    Main ingestion pipeline:
    1. Crawl documentation using Document360-specific crawler
    2. Convert to LangChain Documents
    3. Split documents into chunks
    4. Embed chunks and store them in ChromaDB
    """
    logger.info("--- Starting Ingestion Pipeline ---")

    # 1. Crawl documentation
    documents = crawl_documentation()
    if not documents:
        logger.error("No documents were crawled. Halting ingestion.")
        return

    # 2. Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # 3. Create embeddings and store in ChromaDB
    logger.info("Initializing embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    logger.info("Creating and persisting vector store...")
    # Chroma.from_documents will handle the embedding and storage process
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    
    logger.info(f"--- Ingestion Complete! Vector store saved to {DB_PATH} ---")

if __name__ == "__main__":
    main()