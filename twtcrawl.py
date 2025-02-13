import json
import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
accounts = [
    {"username": "cassassinate", "password": "020601asra!"},
    {"username": "cassdotipynb", "password": "020601asra!"},
    {"username": "nastasya_flipp", "password": "020601asra!"}
    # Add more accounts as needed
]


BASE_URL = "https://x.com/cassdotipynb"  # Adjust as needed
USERNAME = "cassdotipynb" 
PASSWORD = "020601asra!"
def initialize_driver():
    """Initialize the Selenium WebDriver."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Adjust as needed
        chrome_options.add_argument("--log-level=3")  # Suppress ChromeDriver logs
        chrome_options.add_argument("--disable-logging")  # Disable logging
        chrome_options.add_argument("--mute-audio")  # Mute audio to avoid media-related issues
        #chrome_options.add_argument("--headless")

        service = Service("C:/Users/asrah/AppData/Local/Programs/Python/Launcher/chromedriver-win64/chromedriver.exe")
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    except WebDriverException as e:
        print(f"WebDriverException: {e}")
        return None
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None

def navigate_to_profile(driver):
    """Navigate to the profile button after logging in."""
    try:
        # Wait until the profile button is clickable
        profile_button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,))
        )
        profile_button.click()
        print("Navigated to profile.")
    except Exception as e:
        print(f"Error navigating to profile: {e}")
def scroll_and_collect(driver, max_scrolls=150):
    """Scroll down and collect all text from Tumblr posts, excluding retweets and 'You resposted' posts."""
    all_posts = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    unchanged_scrolls = 0  # Counter for unchanged scroll height

    for scroll_num in range(max_scrolls):
        print(f"Scrolling... {scroll_num + 1}/{max_scrolls}")

        # Scroll to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)  # Allow content to load

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        posts = soup.find_all("article")  # Adjust tag if needed

        # Extract data from each post
        for idx, post in enumerate(posts):
            # Skip retweets by checking for the specific retweet span class
            retweet_span = post.find('span', class_='css-1jxf684 r-8akbws r-krxsd3 r-dnmrzs r-1udh08x r-1udbk01 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-n6v787 r-1cwl3u0 r-b88u0q')
            if retweet_span:
                print("Skipping retweet post")
                continue  # Skip this retweet post

            # Skip posts with 'You resposted' in socialContext span
            social_context = post.find('span', {'data-testid': 'socialContext'})
            if social_context and "You resposted" in social_context.get_text():
                print("Skipping reposted post")
                continue  # Skip this reposted post

            # Find the <div> with the specified class containing the text
            post_content_div = post.find('div', class_='css-146c3p1 r-8akbws r-krxsd3 r-dnmrzs r-1udh08x r-1udbk01 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-bnwqim')
            if not post_content_div:
                continue

            # Extract the text content from the <div>
            post_text = post_content_div.get_text(strip=True)
            if post_text and post_text not in all_posts:
                all_posts.append(post_text)

        # Save progress periodically
        if scroll_num % 10 == 0:
            with open("twitter_text_posts_temp.json", "w", encoding="utf-8") as temp_file:
                json.dump(all_posts, temp_file, ensure_ascii=False, indent=4)

        # Check if scrolling has reached the bottom
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            unchanged_scrolls += 1
            print(f"Scroll height unchanged for {unchanged_scrolls} consecutive attempts.")
            if unchanged_scrolls >= 25:  # Stop if unchanged for 25 consecutive attempts
                print("Reached the bottom of the page. No more content to load.")
                break
        else:
            unchanged_scrolls = 0  # Reset counter if height changes

        last_height = new_height

    return all_posts
def login_to_twitter(driver):
    """Automates the login process to Twitter without cookies."""
    print("Navigating to Twitter login page...")
    driver.get(BASE_URL)

    try:
        # Step 1: Wait for the username input field
        print("Waiting for the username field...")
        username_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        print("Username field found. Entering username.")
        username_field.send_keys(USERNAME)
        username_field.send_keys(Keys.RETURN)

        # Step 2: Wait for the password input field
        print("Waiting for the password field...")
        password_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        print("Password field found. Entering password.")
        password_field.send_keys(PASSWORD)
        password_field.send_keys(Keys.RETURN)

        # Step 3: Wait for login to complete by checking for a key element on the homepage
        print("Waiting for login to complete...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]'))  # Tweet button
        )
        print("Login successful.")
        return True

    except Exception as e:
        # Debugging output
        print(f"Login failed: {e}")
        driver.save_screenshot("login_failed.png")  # Save a screenshot for debugging
        print("Screenshot saved as 'login_failed.png'.")
        print(f"Current URL: {driver.current_url}")
        return False

def main():
    driver = initialize_driver()
    if driver is None:
        return

    try:
        if not login_to_twitter(driver):
            return
        
        all_posts = scroll_and_collect(driver)
        with open("twitter_text_posts.json", "w", encoding="utf-8") as f:
            json.dump(all_posts, f, ensure_ascii=False, indent=4)
        print("Data saved to 'twitter_text_posts.json'.")
    finally:
        driver.quit()
if __name__ == "__main__":
    main()



