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
        driver.get('https://twitter.com/i/flow/login')
        time.sleep(6)
        email = driver.find_element_by_name('text')
        email.send_keys(self.email)
        email.send_keys(Keys.ENTER)
        time.sleep(3)
        password = driver.find_element_by_name("password")
        password.send_keys(self.password)
        password.send_keys(Keys.ENTER)
        time.sleep(6)
        driver.get("https://twitter.com/home")  # Redirect to the home page after login
        time.sleep(5)
        self.is_logged_in = True

    def retweet_and_like(self):
        if not self.is_logged_in:
            raise Exception("You must log in first!")

        while True:
            try:
                retweet_button = driver.find_element_by_xpath("//div[@data-testid='retweet']/div")
                retweet_button.click()
                time.sleep(1)

                confirm_retweet_button = driver.find_element_by_xpath("//div[@data-testid='retweetConfirm']/div")
                confirm_retweet_button.click()
                time.sleep(2)

                like_button = driver.find_element_by_xpath("//div[@data-testid='like']/div")
                like_button.click()

                time.sleep(2)
            except NoSuchElementException:
                break

    def search(self, query=''):
        if not self.is_logged_in:
            raise Exception("You must log in first!")

        bot = self.bot

        try:
            searchbox = bot.find_element(By.XPATH, "//input[@data-testid='SearchBox_Search_Input']")
        except NoSuchElementException:
            time.sleep(2)
            searchbox = bot.find_element(By.XPATH, "//input[@data-testid='SearchBox_Search_Input']")

        searchbox.clear()
        searchbox.send_keys(query)
        searchbox.send_keys(Keys.RETURN)
        time.sleep(10)

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
