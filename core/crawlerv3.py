import time
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. CONFIGURATION ---
BASE_URL = "https://docs.overview.ai"
START_URL = "https://docs.overview.ai/docs" # Start at the main docs page to see all products
TARGET_PRODUCT = "OV20i" # We will filter to only scrape this product's docs

# --- 2. SELECTORS ---
NAV_MENU_SELECTOR = "ul#categories.leftsidebarnav"
ARTICLE_LINK_SELECTOR = "ul li a"
ARTICLE_LINK_TEXT_SELECTOR = "span.article-title"
ARTICLE_CONTENT_SELECTOR = "div.content"  # More reliable content selector
ARTICLE_HEADING_SELECTOR = "h1"

# --- 3. HELPER FUNCTIONS ---
def setup_driver():
    """Setup headless Chrome driver for Selenium"""
    print("Setting up Selenium WebDriver...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("WebDriver is ready.")
    return driver

def get_all_article_links(driver, start_url):
    """
    Loads the main docs page with Selenium, waits for the nav to render,
    and extracts all article links with their metadata (product, category).
    """
    print(f"Discovering all article links from: {start_url}")
    all_links = []
    try:
        driver.get(start_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, NAV_MENU_SELECTOR)))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        nav_menu = soup.select_one(NAV_MENU_SELECTOR)
        
        current_product = "General"
        for item in nav_menu.find_all('li', recursive=False):
            # Check for product-level headings like OV20i
            product_link = item.find('a', class_='bubble-menu-link', recursive=False)
            if product_link and 'OV' in product_link.text:
                current_product = product_link.text.strip()

            # Find categories and their articles
            category_headers = item.select('li.article-title-container')
            for category_header in category_headers:
                category_name_tag = category_header.find('a')
                category_name = category_name_tag.text.strip() if category_name_tag else "Uncategorized"

                article_list_ul = category_header.find_next_sibling('ul') or category_header.find('ul')
                if article_list_ul:
                    for link_tag in article_list_ul.select(ARTICLE_LINK_SELECTOR):
                        text_span = link_tag.select_one(ARTICLE_LINK_TEXT_SELECTOR)
                        if link_tag.has_attr('href') and text_span:
                            full_url = urljoin(BASE_URL, link_tag['href'])
                            article_title = text_span.text.strip()
                            all_links.append({
                                "url": full_url,
                                "metadata": {"product": current_product, "category": category_name, "title": article_title}
                            })
    except Exception as e:
        print(f"Error discovering links: {e}")
    return all_links

def scrape_single_article(driver, article_info):
    """
    Scrapes a single article page using Selenium, using the robust logic from your script.
    """
    url = article_info['url']
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ARTICLE_CONTENT_SELECTOR)))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Scrape title
        title_tag = soup.select_one(ARTICLE_HEADING_SELECTOR)
        title = title_tag.text.strip() if title_tag else article_info['metadata']['title']

        # Scrape content
        content_div = soup.select_one(ARTICLE_CONTENT_SELECTOR)
        if content_div:
            # Clean out scripts/styles
            for script in content_div(["script", "style"]):
                script.decompose()
            # Get text and clean it up
            content = content_div.get_text(separator='\n', strip=True)
            cleaned_content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])
            
            if len(cleaned_content) > 20: # Use a smaller threshold to not miss short pages
                # Combine metadata with scraped content
                final_data = article_info['metadata']
                final_data['source'] = url
                final_data['title'] = title # Overwrite nav title with page H1
                final_data['content'] = cleaned_content
                return final_data
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    print("Starting targeted crawl of Overview.ai docs...")
    driver = setup_driver()
    scraped_articles = []
    try:
        # Step 1: Discover ALL links from the rendered navigation menu
        all_links = get_all_article_links(driver, START_URL)
        unique_links = {item['url']: item for item in all_links}.values()

        # Step 2: Filter for ONLY the product we want
        articles_to_scrape = [
            article for article in unique_links 
            if article['metadata']['product'] == TARGET_PRODUCT
        ]
        print(f"\nDiscovered {len(articles_to_scrape)} articles for product '{TARGET_PRODUCT}'. Starting scrape...")
        
        # Step 3: Scrape each of the targeted articles
        for article_info in articles_to_scrape:
            print(f"  -> Scraping: {article_info['url']}")
            scraped_data = scrape_single_article(driver, article_info)
            if scraped_data:
                # NEW: Check if the content is the error message before appending
                if "Limit Exceeded" not in scraped_data['content']:
                    scraped_articles.append(scraped_data)
                    print(f"     ... Success! Content length: {len(scraped_data['content'])}")
                else:
                    print(f"     ... FAILED! Received 'Limit Exceeded' message. Stopping.")
                    # Optional: break the loop if you hit the limit
                    break 
            # THE KEY FIX IS HERE
            time.sleep(2) # SLOW DOWN! Behave more like a human.

        print(f"\nDone! Scraped {len(scraped_articles)} articles for '{TARGET_PRODUCT}'.")
        output_filename = f'scraped_docs_{TARGET_PRODUCT}.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(scraped_articles, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {output_filename}")

    finally:
        print("Closing WebDriver.")
        driver.quit()

# --- Main Execution ---
if __name__ == "__main__":
    TARGET_PRODUCT = "OV20i"
    scraped_articles = []

    # --- PHASE 1: DISCOVERY ---
    print("--- PHASE 1: Discovering all article URLs ---")
    driver = setup_driver()
    articles_to_scrape = []
    try:
        all_links = get_all_article_links(driver, START_URL)
        unique_links = {item['url']: item for item in all_links}.values()
        articles_to_scrape = [
            article for article in unique_links 
            if article['metadata']['product'] == TARGET_PRODUCT
        ]
        print(f"Discovered {len(articles_to_scrape)} articles for product '{TARGET_PRODUCT}'.")
    finally:
        print("Discovery complete. Closing first driver to reset session.")
        driver.quit()

    # --- THE "COOL DOWN" ---
    if articles_to_scrape:
        cool_down_seconds = 30
        print(f"\n--- COOLING DOWN for {cool_down_seconds} seconds to avoid rate limits ---")
        time.sleep(cool_down_seconds)

        # --- PHASE 2: SCRAPING ---
        print("\n--- PHASE 2: Starting slow scrape with a new session ---")
        # Start a brand new, clean driver
        driver = setup_driver()
        try:
            for article_info in articles_to_scrape:
                print(f"  -> Scraping: {article_info['url']}")
                scraped_data = scrape_single_article(driver, article_info)
                if scraped_data:
                    if "Limit Exceeded" not in scraped_data['content']:
                        scraped_articles.append(scraped_data)
                        print(f"     ... Success! Content length: {len(scraped_data['content'])}")
                    else:
                        print(f"     ... FAILED! Hit rate limit again. Stopping scrape.")
                        break
                # Be very patient between scrapes
                time.sleep(5) # Using a very safe 5-second delay
        finally:
            print("Scraping finished. Closing second driver.")
            driver.quit()

    # --- Save the results ---
    output_filename = f'scraped_docs_{TARGET_PRODUCT}.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(scraped_articles, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Done! Scraped {len(scraped_articles)} articles.")
    print(f"Data saved to {output_filename}")