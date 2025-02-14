import requests
from bs4 import BeautifulSoup
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

BASE_URL = "https://cassassinate123.tumblr.com"

def initialize_driver():
    """Initialize the Selenium WebDriver with proper SSL handling"""
    chrome_options = Options()
    # Add essential options for SSL handling
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Update driver path for Windows (adjust if using Linux/Mac)
    chromedriver_path = "C:/Users/asrah/AppData/Local/Programs/Python/Launcher/chromedriver-win64/chromedriver.exe"
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"Chromedriver not found at {chromedriver_path}")

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def is_reblog(post_container):
    """Improved reblog detection"""
    return any([
        post_container.find('div', class_='reblogged-header'),
        post_container.find('a', {'data-action': 'reblog'}),
        post_container.find('span', class_='reblog-icon')
    ])

def scroll_and_collect(driver, max_scrolls=50, scroll_pause=3):
    """More reliable scrolling and content collection"""
    all_posts = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    # Wait for initial content load
    time.sleep(5)

    for _ in range(max_scrolls):
        # Scroll using JavaScript for better reliability
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        
        # Check for content
        soup = BeautifulSoup(driver.page_source, "html.parser")
        post_containers = soup.find_all('article', class_='post') or soup.find_all('div', class_='post')
        
        if not post_containers:
            print("No posts found - check selectors or page structure")
            break
            
        for container in post_containers:
            if is_reblog(container):
                continue
                
            # Extract text with better filtering
            post_text = ' '.join([p.get_text(strip=True) 
                                for p in container.find_all(['p', 'h1', 'h2', 'h3'])
                                if p.get_text(strip=True)])
            if post_text:
                all_posts.append(post_text)

        # Height check with tolerance
        new_height = driver.execute_script("return document.body.scrollHeight")
        if abs(new_height - last_height) < 100:
            print("Reached end of content")
            break
        last_height = new_height

    return all_posts

def main():
    try:
        driver = initialize_driver()
        # Access via HTTPS explicitly
        driver.get(BASE_URL.replace("http://", "https://"))
        
        print("Starting to scrape...")
        all_posts = scroll_and_collect(driver, max_scrolls=20, scroll_pause=4)
        print(f"Scraped {len(all_posts)} text posts from original content.")
        
        with open("tumblr_text_posts.json", "w", encoding="utf-8") as f:
            json.dump(all_posts, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()