import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- STEP 1: CONFIGURATION (Based on your screenshots) ---
BASE_URL = "https://docs.overview.ai"
# We start at the homepage to find all product categories
START_URL = "https://docs.overview.ai/docs/user-manual" 

# It's good practice to identify your crawler
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
}

# --- STEP 2: SELECTORS (Updated based on actual HTML structure) ---

# Selector for the entire left-side navigation bar
NAV_MENU_SELECTOR = "ul#categories.leftsidebarnav"

# Selector for category index items (the main sections)
CATEGORY_INDEX_SELECTOR = "li.article-title-container"

# Selector for article links within categories
ARTICLE_LINK_SELECTOR = "a"

# Selector for article titles in navigation
ARTICLE_TITLE_SELECTOR = "span.article-title"

# Selector for the main article content
ARTICLE_CONTENT_SELECTOR = "div.content_block_text"

# Selector for the main article title/heading
ARTICLE_HEADING_SELECTOR = "h1"

# --- STEP 3: HELPER FUNCTIONS ---

def setup_driver():
    """Setup headless Chrome driver for Selenium"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_article_content(url, driver):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ARTICLE_CONTENT_SELECTOR)))
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title_tag = soup.select_one(ARTICLE_HEADING_SELECTOR)
        title = title_tag.text.strip() if title_tag else url
        content_divs = soup.select(ARTICLE_CONTENT_SELECTOR)
        content_div = None
        for div in content_divs:
            text_content = div.get_text(strip=True)
            if len(text_content) > 100:
                content_div = div
                break
        if content_div:
            for script in content_div(["script", "style"]):
                script.decompose()
            content = content_div.get_text(separator='\n', strip=True)
            lines = content.split('\n')
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            cleaned_content = '\n'.join(cleaned_lines)
            if len(cleaned_content) > 50:
                return {
                    'url': url,
                    'title': title,
                    'content': cleaned_content
                }
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def get_all_article_links_and_scrape(start_url, driver):
    visited = set()
    scraped_articles = []

    def crawl(url):
        if url in visited:
            return
        visited.add(url)
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            nav_menu = soup.select_one(NAV_MENU_SELECTOR)
            links = []
            if nav_menu:
                for a in nav_menu.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = urljoin(BASE_URL, href)
                    else:
                        full_url = urljoin(url, href)
                    if full_url.startswith(BASE_URL):
                        links.append(full_url)
            # Scrape this page for content
            article = scrape_article_content(url, driver)
            if article:
                scraped_articles.append(article)
                print(f"  -> Article: {url} (content length: {len(article['content'])})")
            # Recurse into all sidebar links
            for l in links:
                if l not in visited:
                    crawl(l)
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return

    crawl(start_url)
    return scraped_articles

def main():
    print("Starting OV20i sidebar recursive crawl (all pages, save if content)...")
    driver = setup_driver()
    try:
        scraped_articles = get_all_article_links_and_scrape(START_URL, driver)
        print(f"Done! Scraped {len(scraped_articles)} articles.")
        with open('scraped_docs_overview_ai.json', 'w', encoding='utf-8') as f:
            json.dump(scraped_articles, f, indent=2, ensure_ascii=False)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()