from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()

chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1200")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)

class TwitterBot:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.bot = driver
        self.is_logged_in = False

    def login(self):
        driver.get('https://twitter.com')
        time.sleep(5)
    
        fb_btn = driver.find_element(By.XPATH, '/html/body/div/div/div/div[2]/main/div/div/div[1]/div[1]/div/div[3]/div[5]/a/div/span/span')
        fb_btn.click()
        time.sleep(5)
    
        # Wait for the username field to be present
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input'))
        )
        username_field.send_keys(username)
        
        next_button = driver.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div')
        next_button.click()
        time.sleep(5)
        
        # Wait for the password field to be present
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input'))
        )
        password_field.send_keys(password)
    
        password_field.send_keys(Keys.RETURN)
        self.is_logged_in = True

    
    def retweet_and_like(self):
        if not self.is_logged_in:
            raise Exception("You must log in first!")

        while True:
            try:
                retweet_button = self.bot.find_element_by_xpath("//div[@data-testid='retweet']/div")
                retweet_button.click()
                time.sleep(1)

                confirm_retweet_button = self.bot.find_element_by_xpath("//div[@data-testid='retweetConfirm']/div")
                confirm_retweet_button.click()
                time.sleep(2)

                like_button = self.bot.find_element_by_xpath("//div[@data-testid='like']/div")
                like_button.click()

                time.sleep(2)
            except NoSuchElementException:
                break

    def search(self, keyword):
        bot = self.bot

            search_query = f"{keyword} -filter:retweets -filter:replies filter:images filter:safe"
    driver.get(f"https://twitter.com/search?q=%23{search_query}&src=recent_search_click&f=live")
    
    # Scroll down to load more tweets
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
    
        # Wait for the tweets to load
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="tweet"]')))
        except:
            print(f"No tweets found for {keyword}")
    
        # Extract posts
        likes = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='like']")))
        retweets = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='retweet']")))
    
        print("Found:", len(likes), "posts to like!")
        print("Found:", len(retweets), "posts to retweet!")
    
# Replace 'YOUR_EMAIL' and 'YOUR_PASSWORD' with your Twitter credentials
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
twitter_bot = TwitterBot(email=username, password=password)
twitter_bot.login()

# List of keywords to search and interact with
keywords_list = ['#CatsOfTwitter', '#DogsOfTwitter', '#Caturday', '#CatsOnTwitter', '#DogsOnTwitter']

for keyword in keywords_list:
    twitter_bot.search(keyword)
    time.sleep(5)  # Adjust sleep time as needed
    twitter_bot.retweet_and_like()
