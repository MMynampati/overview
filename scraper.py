import requests
from bs4 import BeautifulSoup
import chromadb
from sentence_transformers import SentenceTransformer
import os
from typing import List, Dict, Tuple
import re
from urllib.parse import urljoin, urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManualPageScraper:
    def __init__(self, db_path: str = "./data/chroma_db"):
        """Initialize the scraper with ChromaDB for vector storage."""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Try to get existing collection, create if it doesn't exist
        try:
            self.collection = self.client.get_collection("manual_pages")
        except:
            self.collection = self.client.create_collection("manual_pages")
        
        # Initialize sentence transformer for embeddings
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text
    
    def extract_text_from_html(self, html: str, url: str) -> List[Dict[str, str]]:
        """Extract text content from HTML with metadata."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text from different elements
        chunks = []
        
        # Get title
        title = soup.find('title')
        title_text = self.clean_text(title.get_text()) if title else ""
        
        # Get headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            text = self.clean_text(heading.get_text())
            if text and len(text) > 10:  # Only keep substantial headings
                chunks.append({
                    'text': text,
                    'type': 'heading',
                    'url': url,
                    'title': title_text
                })
        
        # Get paragraphs
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = self.clean_text(p.get_text())
            if text and len(text) > 20:  # Only keep substantial paragraphs
                chunks.append({
                    'text': text,
                    'type': 'paragraph',
                    'url': url,
                    'title': title_text
                })
        
        # Get list items
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            for item in items:
                text = self.clean_text(item.get_text())
                if text and len(text) > 10:
                    chunks.append({
                        'text': text,
                        'type': 'list_item',
                        'url': url,
                        'title': title_text
                    })
        
        return chunks
    
    def scrape_page(self, url: str) -> List[Dict[str, str]]:
        """Scrape a single page and return text chunks."""
        try:
            logger.info(f"Scraping: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            chunks = self.extract_text_from_html(response.text, url)
            logger.info(f"Extracted {len(chunks)} chunks from {url}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return []
    
    def index_pages(self, urls: List[str]) -> None:
        """Index multiple pages into the vector database."""
        all_chunks = []
        
        for url in urls:
            chunks = self.scrape_page(url)
            all_chunks.extend(chunks)
        
        if not all_chunks:
            logger.warning("No content extracted from any pages")
            return
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(all_chunks):
            doc_id = f"doc_{i}_{hash(chunk['url'])}"
            
            documents.append(chunk['text'])
            metadatas.append({
                'url': chunk['url'],
                'title': chunk['title'],
                'type': chunk['type']
            })
            ids.append(doc_id)
        
        # Add to ChromaDB
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Indexed {len(all_chunks)} chunks from {len(urls)} pages")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search the indexed content for relevant chunks."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'text': results['documents'][0][i],
                'url': results['metadatas'][0][i]['url'],
                'title': results['metadatas'][0][i]['title'],
                'type': results['metadatas'][0][i]['type'],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results
    
    def get_all_urls(self) -> List[str]:
        """Get all unique URLs in the database."""
        results = self.collection.get()
        urls = set()
        for metadata in results['metadatas']:
            urls.add(metadata['url'])
        return list(urls)

if __name__ == "__main__":
    # Example usage
    scraper = ManualPageScraper()
    
    # Example URLs - replace with your actual manual page URLs
    urls = [
        "https://example.com/manual1",
        "https://example.com/manual2"
    ]
    
    scraper.index_pages(urls) 