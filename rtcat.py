from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
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
        bot = self.bot
        bot.get('https://twitter.com/')
        time.sleep(4)

        try:
            email_input = bot.find_element(By.NAME, 'session[username_or_email]')
            password_input = bot.find_element(By.NAME, 'session[password]')
        except NoSuchElementException:
            time.sleep(3)
            email_input = bot.find_element(By.NAME, 'session[username_or_email]')
            password_input = bot.find_element(By.NAME, 'session[password]')

        email_input.clear()
        password_input.clear()
        email_input.send_keys(self.email)
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(10)
        self.is_logged_in = True

    def logout(self):
        if not self.is_logged_in:
            return

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
    
# Logout
twitter_bot.logout()
