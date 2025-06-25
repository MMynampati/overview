import requests
from bs4 import BeautifulSoup

def test_navigation():
    url = "https://docs.overview.ai/docs/user-manual"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for the navigation menu
        nav_menu = soup.select_one("ul#categories.leftsidebarnav")
        print(f"Navigation menu found: {nav_menu is not None}")
        
        if nav_menu:
            print(f"Navigation menu HTML (first 500 chars): {str(nav_menu)[:500]}")
            
            # Look for different possible selectors
            selectors_to_try = [
                "li.article-title-container",
                "li",
                "a",
                "span.article-title"
            ]
            
            for selector in selectors_to_try:
                elements = nav_menu.select(selector)
                print(f"Selector '{selector}': found {len(elements)} elements")
                if elements:
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        print(f"  {i}: {elem.get('class', 'no-class')} - {str(elem)[:100]}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_actual_url():
    url = "https://docs.overview.ai/docs/start-here"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for the content div
        content_div = soup.select_one("div.content_block_text")
        print(f"Content div found: {content_div is not None}")
        
        if content_div:
            print(f"Content div HTML (first 500 chars): {str(content_div)[:500]}")
            
            # Check for different content selectors
            selectors_to_try = [
                "div.content_block_text",
                "div.article-content",
                "div.content_container_text_sec",
                "div.content_block_text div",
                "div.content_block_text p",
                "div.content_block_text h1",
                "div.content_block_text h2",
                "div.content_block_text ul",
                "div.content_block_text li"
            ]
            
            for selector in selectors_to_try:
                elements = soup.select(selector)
                print(f"Selector '{selector}': found {len(elements)} elements")
                if elements:
                    for i, elem in enumerate(elements[:2]):  # Show first 2
                        text_content = elem.get_text(strip=True)
                        print(f"  {i}: Text length: {len(text_content)}, Preview: {text_content[:100]}")
        else:
            print("No content div found!")
            # Try to find any div with content
            all_divs = soup.find_all('div')
            print(f"Total divs found: {len(all_divs)}")
            for i, div in enumerate(all_divs[:5]):  # Show first 5 divs
                print(f"Div {i}: {div.get('class', 'no-class')} - {str(div)[:100]}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_navigation()
    test_actual_url() 