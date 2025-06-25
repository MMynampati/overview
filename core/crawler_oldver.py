# core/crawler.py
import requests
import xml.etree.ElementTree as ET
import logging
from typing import List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_urls_from_sitemap(sitemap_url: str) -> List[str]:
    """
    Fetches and parses a sitemap.xml to extract all URLs.

    Args:
        sitemap_url: The full URL to the sitemap.xml file.

    Returns:
        A list of URLs found in the sitemap.
    """
    urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; MyDocsBot/1.0; +http://mydomain.com/bot.html)'
    }
    try:
        response = requests.get(sitemap_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        root = ET.fromstring(response.content)
        # The namespace is crucial for parsing sitemaps correctly
        namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        for url_element in root.findall('sitemap:url', namespace):
            loc_element = url_element.find('sitemap:loc', namespace)
            if loc_element is not None and loc_element.text:
                urls.append(loc_element.text)

        logger.info(f"Successfully found {len(urls)} URLs in sitemap: {sitemap_url}")
        return urls

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching sitemap {sitemap_url}: {e}")
        return []
    except ET.ParseError as e:
        logger.error(f"Error parsing XML from sitemap {sitemap_url}: {e}")
        return []

def get_urls_from_list(url_list: str) -> List[str]:
    """
    Parses a comma-separated list of URLs.

    Args:
        url_list: Comma-separated string of URLs.

    Returns:
        A list of URLs from the string.
    """
    if not url_list:
        return []
    
    urls = [url.strip() for url in url_list.split(',') if url.strip()]
    logger.info(f"Successfully parsed {len(urls)} URLs from manual list")
    return urls