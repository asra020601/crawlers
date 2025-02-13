import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
BASE_URL = "https://twitter.com/login"

# List of accounts with usernames and passwords
ACCOUNTS  = [{"username": "cassassinate", "password": "020601asra!", "profile_url": "https://x.com/cassassinate"},
    {"username": "cassdotipynb", "password": "020601asra!",  "profile_url":"https://x.com/cassdotipynb"},
    {"username": "nastasya_flipp", "password": "020601asra!", "profile_url": "https://x.com/nastasya_flipp"}]

def initialize_driver():
    """Initialize the Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Uncomment below for headless mode
    chrome_options.add_argument("--headless")  

    try:
        service = Service("C:/Users/asrah/AppData/Local/Programs/Python/Launcher/chromedriver-win64/chromedriver.exe")  # Replace with your Chromedriver path
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None

def login_to_twitter(driver, username, password):
    """Automates the login process to Twitter."""
    print(f"Logging in with username: {username}")
    driver.get(BASE_URL)

    try:
        print("Waiting for the username field...")
        username_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)

        print("Waiting for the password field...")
        password_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        print("Waiting for login to complete...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]'))
        )
        print(f"Login successful for {username}.")
        return True

    except Exception as e:
        print(f"Login failed for {username}: {e}")
        return False

def navigate_to_profile(driver, profile_url):
    """Navigate to a specific Twitter profile."""
    print(f"Navigating to profile: {profile_url}")
    driver.get(profile_url)
    time.sleep(5)  # Wait for the profile page to load

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

def scroll_and_collect(driver, creation_date, max_scrolls=150):
    """
    Scroll and collect tweets until reaching the account creation date.

    Args:
        driver: Selenium WebDriver instance.
        creation_date: Account creation date as a datetime object.
        max_scrolls: Maximum number of scrolls.

    Returns:
        List of collected tweets.
    """
    print("Starting tweet collection...")
    tweets = []
    scroll_count = 0
    last_height = driver.execute_script("return document.body.scrollHeight")

    while scroll_count < max_scrolls:
        try:
            # Extract tweets in the current view
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
            )
            for element in elements:
                try:
                    # Extract tweet text
                    tweet_text = element.find_element(By.CSS_SELECTOR, '[lang]').text

                    # Extract timestamp
                    timestamp_element = element.find_element(By.CSS_SELECTOR, 'time')
                    tweet_date = timestamp_element.get_attribute("datetime")  # ISO 8601 format
                    tweet_date = datetime.fromisoformat(tweet_date.replace("Z", "+00:00"))

                    # Stop if tweet is older than the account creation date
                    if tweet_date < creation_date:
                        print("Reached account creation date. Stopping scroll.")
                        return tweets

                    # Add only unique tweets
                    if tweet_text and {"text": tweet_text, "date": tweet_date.isoformat()} not in tweets:
                        tweets.append({"text": tweet_text, "date": tweet_date.isoformat()})
                except Exception as e:
                    print(f"Error processing tweet: {e}")
                    continue

            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for new content to load
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:  # No change in height means no more content
                print("No new content detected. Exiting scroll.")
                break

            last_height = new_height
            scroll_count += 1

        except TimeoutException:
            print("Timeout waiting for tweet elements. Retrying...")
            break

    print(f"Completed scrolling after {scroll_count} scrolls.")
    return tweets

def main():
    for account in ACCOUNTS:
        driver = initialize_driver()
        if driver is None:
            continue

        try:
            if login_to_twitter(driver, account["username"], account["password"]):
                # Navigate to the target profile page
                navigate_to_profile(driver, account["profile_url"])

                # Parse creation date
                creation_date = datetime.strptime(account["creation_date"], "%Y-%m-%d")

                # Collect tweets from the profile page
                all_posts = scroll_and_collect(driver, creation_date)

                # Save data in the required JS-like format
                profile_name = account["profile_url"].split("/")[-1]
                file_name = f"{profile_name}_tweets.json"
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(all_posts, f, ensure_ascii=False, indent=4)
                print(f"Data saved to '{file_name}'.")
        finally:
            driver.quit()
