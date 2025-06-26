# ingest.py
import logging
import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

# Import our crawler functions
from core.crawler import load_urls_from_csv, scrape_url_list, setup_driver

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
CSV_FILE = "core/overview.csv"
DB_PATH = os.getenv('DB_PATH', 'vectorstore')
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

def load_scraped_data():
    """
    Load scraped data from the JSON file created by the crawler.
    Returns a list of LangChain Document objects.
    """
    logger.info("--- Loading Scraped Data ---")
    
    json_file = 'scraped_docs_overview_ai.json'
    if not os.path.exists(json_file):
        logger.error(f"Scraped data file {json_file} not found. Please run the crawler first.")
        return []
    
    with open(json_file, 'r', encoding='utf-8') as f:
        scraped_articles = json.load(f)
    
    logger.info(f"Loaded {len(scraped_articles)} articles from {json_file}")
    
    # Convert to LangChain Documents
    documents = []
    for article in scraped_articles:
        doc = Document(
            page_content=article['content'],
            metadata={
                'source': article['url'],
                'title': article['title'],
                'category': article.get('category', 'Unknown')
            }
        )
        documents.append(doc)
    
    return documents

def main():
    """
    Main ingestion pipeline:
    1. Load scraped data from JSON file
    2. Convert to LangChain Documents
    3. Split documents into chunks
    4. Embed chunks and store them in ChromaDB
    """
    logger.info("--- Starting Ingestion Pipeline ---")

    # 1. Load scraped data
    documents = load_scraped_data()
    if not documents:
        logger.error("No documents were loaded. Please run the crawler first.")
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