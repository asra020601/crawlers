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
    """Initialize the Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    chromium_path = '/usr/bin/chromium-browser' 
    if os.path.exists(chromium_path):
        chrome_options.binary_location = chromium_path
    else:
        print(f"Warning: Chromium executable not found at '{chromium_path}'.")
        print("Using default ChromeDriver configuration.")
       
    service = Service("C:/Users/asrah/AppData/Local/Programs/Python/Launcher/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def is_reblog(post_container):
    """Check if a post container is a reblog."""
    # Tumblr reblogs typically have a "reblogged" indicator in one of these patterns
    return any([
        post_container.find('div', class_='reblogged_from'),  # Classic theme indicator
        post_container.find('a', class_='reblog_button'),     # Newer theme indicator
        post_container.find('footer', class_='post_notes')     # Notes section
    ])

def scroll_and_collect(driver, max_scrolls=5000, scroll_pause=2):
    """Scroll down and collect text from original posts only."""
    all_posts = []
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find all post containers - adjust selector based on your theme
        post_containers = soup.find_all('article', class_='post') or soup.find_all('div', class_='post')
        
        for container in post_containers:
            if is_reblog(container):
                continue  # Skip reblogs
                
            # Collect text from non-reblog posts
            post_text = [p.get_text(strip=True) 
                        for p in container.find_all('p') 
                        if p.get_text(strip=True)]
            all_posts.extend(post_text)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("No more content to load.")
            break
        last_height = new_height

    return all_posts  # Removed set() to preserve order while deduping

def main():
    driver = initialize_driver()
    driver.get(BASE_URL)

    try:
        print("Starting to scrape...")
        all_posts = scroll_and_collect(driver, max_scrolls=10000, scroll_pause=2)
        print(f"Scraped {len(all_posts)} text posts from original content.")

        with open("tumblr_text_posts.json", "w", encoding="utf-8") as f:
            json.dump(all_posts, f, ensure_ascii=False, indent=4)

        print("Data saved to 'tumblr_text_posts.json'.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()