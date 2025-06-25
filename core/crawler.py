import time
import json
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. YOUR MANUAL DATA ---
# Pasted directly from your input. We will parse this.
manual_data = """
Product	Category	Page Name	Page URL
OV20i	Start Here	Recommended Setup Flow	https://docs.overview.ai/docs/recommended-setup-flow
			https://docs.overview.ai/docs/quick-start-guide
			https://docs.overview.ai/docs/product-activation
			https://docs.overview.ai/docs/basic-navigation
			https://docs.overview.ai/docs/creating-your-first-recipe
			https://docs.overview.ai/docs/creating-your-first-classification-recipe
			https://docs.overview.ai/docs/creating-your-first-segmentation-recipe
		Hardware Setup	https://docs.overview.ai/docs/technical-specifications
			https://docs.overview.ai/docs/recommended-accessories
			https://docs.overview.ai/docs/mounting-and-mechanical
			https://docs.overview.ai/docs/electrical-and-communication
		Walkthroughs	https://docs.overview.ai/docs/creating-a-basic-single-roi-classifier-1
			https://docs.overview.ai/docs/creating-a-segmenter
			https://docs.overview.ai/docs/multiple-views-one-recipe
			https://docs.overview.ai/docs/adding-data-to-an-existing-recipe-and-retraining
			https://docs.overview.ai/docs/trigger-using-a-plc
			https://docs.overview.ai/docs/rs232
			https://docs.overview.ai/docs/tcp-communication
			https://docs.overview.ai/docs/change-recipe-using-plc
			https://docs.overview.ai/docs/communication-troubleshooting
			https://docs.overview.ai/docs/create-a-classifier-node-red-logic-2
			https://docs.overview.ai/docs/recipe-change-using-http
			https://docs.overview.ai/docs/setting-up-mqtt-communication
			https://docs.overview.ai/docs/trigger-using-mqtt-communication
			https://docs.overview.ai/docs/send-customdata-from-plc-to-camera
		Software Setup	https://docs.overview.ai/docs/recipe-management
			https://docs.overview.ai/docs/recipe-editor
			https://docs.overview.ai/docs/imaging-setup
			https://docs.overview.ai/docs/alignment-block
			https://docs.overview.ai/docs/roi-block
			https://docs.overview.ai/docs/classification-block
			https://docs.overview.ai/docs/segmentation-block
			https://docs.overview.ai/docs/io-and-node-red-logic
			https://docs.overview.ai/docs/ftp-server
			https://docs.overview.ai/docs/hmi
			https://docs.overview.ai/docs/library
			https://docs.overview.ai/docs/users-and-permissions
			https://docs.overview.ai/docs/settings
			https://docs.overview.ai/docs/software-update
			https://docs.overview.ai/docs/software-updates-release-notes
		PLC Communication	https://docs.overview.ai/docs/plc-communication-ethernetip-connections
			https://docs.overview.ai/docs/plc-communication-ethernetip-recipe-switch
			https://docs.overview.ai/docs/trigger-using-a-plc-ethernet
			https://docs.overview.ai/docs/ethernetip-setting-up-rockwell-software
			https://docs.overview.ai/docs/plc-communication-profinet
		Robots	
			https://docs.overview.ai/docs/universal-robots
"""

# --- 2. CONFIGURATION & SELECTORS ---
ARTICLE_CONTENT_SELECTOR = "div.content_block_text"
ARTICLE_HEADING_SELECTOR = "h1"

# --- 3. HELPER FUNCTIONS ---
def parse_manual_data(data):
    """Parses the tab-separated text data into a structured list."""
    articles = []
    current_product = ""
    current_category = ""
    
    lines = data.strip().split('\n')
    for line in lines[1:]: # Skip the header row
        parts = line.split('\t')
        
        # Update product if present
        if parts[0].strip():
            current_product = parts[0].strip()
        
        # Update category if present
        if len(parts) > 1 and parts[1].strip():
            current_category = parts[1].strip()
        
        # Find the URL in the line
        url_match = re.search(r'https?://[^\s]+', line)
        if url_match:
            url = url_match.group(0)
            
            # Find the title (text before the URL)
            title = line.split(url)[0].strip().split('\t')[-1]

            articles.append({
                "url": url,
                "metadata": {
                    "product": current_product,
                    "category": current_category,
                    "title": title or "Untitled" # Use title or a fallback
                }
            })
    return articles

def setup_driver():
    """Sets up the Selenium WebDriver."""
    print("Setting up Selenium WebDriver...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_single_article(driver, article_info):
    """Scrapes a single article, using provided metadata."""
    url = article_info['url']
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ARTICLE_CONTENT_SELECTOR)))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        title_tag = soup.select_one(ARTICLE_HEADING_SELECTOR)
        # Use H1 on page, but fall back to the title from our manual list
        title = title_tag.text.strip() if title_tag else article_info['metadata']['title']
        
        content_div = soup.select_one(ARTICLE_CONTENT_SELECTOR)
        if content_div:
            content = content_div.get_text(separator='\n', strip=True)
            if "Limit Exceeded" not in content and len(content) > 20:
                final_data = article_info['metadata']
                final_data['source'] = url
                final_data['title'] = title
                final_data['content'] = content
                return final_data
        return None
    except Exception as e:
        print(f"    - Error scraping {url}: {e}")
        return None

# --- 4. MAIN EXECUTION ---
def main():
    print("--- Parsing manual data list ---")
    articles_to_scrape = parse_manual_data(manual_data)
    if not articles_to_scrape:
        print("ERROR: No articles were parsed from the manual data. Please check the format.")
        return
        
    print(f"Successfully parsed {len(articles_to_scrape)} articles to scrape.")

    driver = setup_driver()
    scraped_articles = []
    
    try:
        total = len(articles_to_scrape)
        for i, article_info in enumerate(articles_to_scrape):
            wait_time = 8
            print(f"\n({i+1}/{total}) Waiting {wait_time}s...")
            time.sleep(wait_time)
            
            print(f"  -> Scraping '{article_info['metadata']['title']}' from {article_info['url']}")
            scraped_data = scrape_single_article(driver, article_info)
            if scraped_data:
                scraped_articles.append(scraped_data)
                print(f"     ... Success! Content length: {len(scraped_data['content'])}")
            else:
                print("     ... Failed or no content found.")
    finally:
        print("\nCrawl finished. Closing driver.")
        driver.quit()

    output_filename = 'scraped_docs_OV20i_with_metadata.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(scraped_articles, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Done! Scraped {len(scraped_articles)} articles.")
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    main()