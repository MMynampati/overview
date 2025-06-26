import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
BASE_URL = "https://docs.overview.ai"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
}

# --- CSV FILE CONFIGURATION ---
CSV_FILE = "core/overview.csv"  # Your updated CSV file name

# --- SELECTORS ---
ARTICLE_CONTENT_SELECTOR = "div.content_block_text"
ARTICLE_HEADING_SELECTOR = "h1"

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

def load_urls_from_csv(csv_file):
    """Load URLs and categories from CSV file"""
    try:
        df = pd.read_csv(csv_file)
        # Remove rows with empty URLs
        df = df.dropna(subset=['Page URL'])
        df = df[df['Page URL'].str.strip() != '']
        
        # Create list of dictionaries with URL and category
        url_data = []
        for _, row in df.iterrows():
            url_data.append({
                'url': row['Page URL'].strip(),
                'category': row['Category'].strip() if pd.notna(row['Category']) else 'Unknown'
            })
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_url_data = []
        for item in url_data:
            if item['url'] not in seen_urls:
                unique_url_data.append(item)
                seen_urls.add(item['url'])
        
        print(f"Loaded {len(unique_url_data)} URLs from {csv_file}")
        return unique_url_data
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return []

def scrape_article_content(url, driver):
    """Scrape content from a single article URL"""
    try:
        print(f"Scraping: {url}")
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ARTICLE_CONTENT_SELECTOR)))
        time.sleep(2)  # Give page time to fully load
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Get title
        title_tag = soup.select_one(ARTICLE_HEADING_SELECTOR)
        title = title_tag.text.strip() if title_tag else url.split('/')[-1]
        
        # Get content
        content_divs = soup.select(ARTICLE_CONTENT_SELECTOR)
        content_div = None
        
        # Find the content div with the most text
        for div in content_divs:
            text_content = div.get_text(strip=True)
            if len(text_content) > 100:  # Only consider divs with substantial content
                content_div = div
                break
        
        if content_div:
            # Clean up the content
            for script in content_div(["script", "style"]):
                script.decompose()
            
            content = content_div.get_text(separator='\n', strip=True)
            lines = content.split('\n')
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            cleaned_content = '\n'.join(cleaned_lines)
            
            if len(cleaned_content) > 50:  # Only return if we have meaningful content
                print(f"  -> Success: {len(cleaned_content)} characters")
                return {
                    'url': url,
                    'title': title,
                    'content': cleaned_content
                }
        
        print(f"  -> No content found")
        return None
        
    except Exception as e:
        print(f"  -> Error scraping {url}: {e}")
        return None

def scrape_url_list(url_data_list, driver):
    """Scrape all URLs in the list"""
    scraped_articles = []
    
    for i, url_data in enumerate(url_data_list, 1):
        url = url_data['url']
        category = url_data['category']
        print(f"[{i}/{len(url_data_list)}] Processing: {url}")
        
        article = scrape_article_content(url, driver)
        if article:
            # Add category to the article data
            article['category'] = category
            scraped_articles.append(article)
        
        # Be nice to the server
        time.sleep(1)
    
    return scraped_articles

def main():
    print("Starting CSV-based URL scraping...")
    
    # Load URLs and categories from CSV
    url_data_list = load_urls_from_csv(CSV_FILE)
    
    if not url_data_list:
        print("No URLs found in CSV file. Exiting.")
        return
    
    print(f"Found {len(url_data_list)} URLs to scrape")
    
    # Show category breakdown
    categories = {}
    for item in url_data_list:
        cat = item['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("Category breakdown:")
    for cat, count in categories.items():
        print(f"  - {cat}: {count} URLs")
    
    driver = setup_driver()
    try:
        scraped_articles = scrape_url_list(url_data_list, driver)
        
        print(f"\nDone! Successfully scraped {len(scraped_articles)} out of {len(url_data_list)} URLs.")
        
        # Save results
        output_file = 'scraped_docs_overview_ai.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scraped_articles, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {output_file}")
        
        # Print summary
        total_chars = sum(len(article['content']) for article in scraped_articles)
        print(f"Total content scraped: {total_chars:,} characters")
        
        # Show success by category
        scraped_by_category = {}
        for article in scraped_articles:
            cat = article['category']
            scraped_by_category[cat] = scraped_by_category.get(cat, 0) + 1
        
        print("\nSuccessfully scraped by category:")
        for cat, count in scraped_by_category.items():
            total_in_cat = categories.get(cat, 0)
            print(f"  - {cat}: {count}/{total_in_cat} URLs")
        
        # Print failed URLs if any
        scraped_urls = set(article['url'] for article in scraped_articles)
        failed_urls = [item for item in url_data_list if item['url'] not in scraped_urls]
        if failed_urls:
            print(f"\nFailed to scrape {len(failed_urls)} URLs:")
            for item in failed_urls:
                print(f"  - {item['url']} ({item['category']})")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()