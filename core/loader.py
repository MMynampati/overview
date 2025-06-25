# core/loader.py
import requests
import time
import logging
from bs4 import BeautifulSoup
from typing import List, Optional
from langchain.schema import Document

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
# Target the specific content area of the Overview AI docs for cleaner text extraction
TARGET_CONTENT_CLASS = "theme-doc-markdown markdown"

class WebContentLoader:
    """
    Scrapes web pages and loads their main content as LangChain Document objects.
    Includes a politeness delay between requests.
    """
    def __init__(self, urls: List[str], delay_seconds: float = 1.0):
        """
        Args:
            urls: A list of URLs to scrape.
            delay_seconds: Time to wait between each HTTP request.
        """
        self.urls = urls
        self.delay = delay_seconds
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; MyDocsBot/1.0; +http://mydomain.com/bot.html)'
        }

    def _scrape_single_page(self, url: str) -> Optional[str]:
        """Scrapes the targeted text content from a single URL."""
        try:
            logger.info(f"Scraping: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Find the main content container. This is KEY for high-quality data.
            content_div = soup.find('div', class_=TARGET_CONTENT_CLASS)

            if content_div:
                # Use .get_text() for clean, structured text extraction.
                # ' ' separator helps maintain word spacing between tags.
                return content_div.get_text(separator=' ', strip=True)
            else:
                logger.warning(f"Could not find target content class '{TARGET_CONTENT_CLASS}' on {url}. Skipping.")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error during request to {url}: {e}")
            return None

    def load(self) -> List[Document]:
        """
        Loads content from all URLs and returns a list of LangChain Documents.
        """
        documents = []
        for url in self.urls:
            content = self._scrape_single_page(url)
            if content:
                # Create a LangChain Document for each successfully scraped page.
                # The metadata is crucial for citing sources later.
                doc = Document(
                    page_content=content,
                    metadata={"source": url}
                )
                documents.append(doc)
            
            # Politeness delay
            logger.info(f"Waiting for {self.delay} seconds before next request...")
            time.sleep(self.delay)
            
        logger.info(f"Successfully scraped and created {len(documents)} documents.")
        return documents