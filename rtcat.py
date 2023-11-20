from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException 
from selenium.common.exceptions import NoSuchElementException
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


    def login(username, password):
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
        time.sleep(10)


        bot = self.bot
        bot.get('https://twitter.com/home')
        time.sleep(4)

        try:
            bot.find_element(By.XPATH, "//div[@data-testid='SideNav_AccountSwitcher_Button']").click()
        except NoSuchElementException:
            time.sleep(3)
            bot.find_element(By.XPATH, "//div[@data-testid='SideNav_AccountSwitcher_Button']").click()

        time.sleep(1)

        try:
            bot.find_element(By.XPATH, "//a[@data-testid='AccountSwitcher_Logout_Button']").click()
        except NoSuchElementException:
            time.sleep(2)
            bot.find_element(By.XPATH, "//a[@data-testid='AccountSwitcher_Logout_Button']").click()

        time.sleep(3)

        try:
            bot.find_element(By.XPATH, "//div[@data-testid='confirmationSheetConfirm']").click()
        except NoSuchElementException:
            time.sleep(3)
            bot.find_element(By.XPATH, "//div[@data-testid='confirmationSheetConfirm']").click()

        time.sleep(3)
        self.is_logged_in = False

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

    def like_tweets(self, cycles=10):
        if not self.is_logged_in:
            raise Exception("You must log in first!")

        bot = self.bot

        for i in range(cycles):
            try:
                bot.find_element(By.XPATH, "//div[@data-testid='like']").click()
            except NoSuchElementException:
                time.sleep(3)
                bot.execute_script('window.scrollTo(0,document.body.scrollHeight/1.5)')
                time.sleep(3)
                bot.find_element(By.XPATH, "//div[@data-testid='like']").click()

            time.sleep(1)
            bot.execute_script('window.scrollTo(0,document.body.scrollHeight/1.5)')
            time.sleep(5)

    def post_tweets(self, tweetBody):
        if not self.is_logged_in:
            raise Exception("You must log in first!")

        bot = self.bot

        try:
            bot.find_element(By.XPATH, "//a[@data-testid='SideNav_NewTweet_Button']").click()
        except NoSuchElementException:
            time.sleep(3)
            bot.find_element(By.XPATH, "//a[@data-testid='SideNav_NewTweet_Button']").click()

        time.sleep(4)
        body = tweetBody

        try:
            bot.find_element(By.XPATH, "//div[@role='textbox']").send_keys(body)
        except NoSuchElementException:
            time.sleep(3)
            bot.find_element(By.XPATH, "//div[@role='textbox']").send_keys(body)

        time.sleep(4)
        bot.find_element(By.CLASS_NAME, "notranslate").send_keys(Keys.ENTER)
        bot.find_element(By.XPATH, "//div[@data-testid='tweetButton']").click()
        time.sleep(4)

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
    twitter_bot.like_tweets(cycles=1)
