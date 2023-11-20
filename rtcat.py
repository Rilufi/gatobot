from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from pyvirtualdisplay import Display
import time
import os

display = Display(visible=0, size=(800, 800))  
display.start()

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

chrome_options = webdriver.ChromeOptions()    
# Add your options as needed    
options = [
  # Define window size here
   "--window-size=1200,1200",
    "--ignore-certificate-errors"
 
    #"--headless",
    #"--disable-gpu",
    #"--window-size=1920,1200",
    #"--ignore-certificate-errors",
    #"--disable-extensions",
    #"--no-sandbox",
    #"--disable-dev-shm-usage",
    #'--remote-debugging-port=9222'
]

for option in options:
    chrome_options.add_argument(option)

    
driver = webdriver.Chrome(options = chrome_options)

def login(username, password):
    # Open Twitter
    driver.get('https://twitter.com')
    # Wait for the login page to load
    time.sleep(5)

    fb_btn = driver.find_element("xpath", '/html/body/div/div/div/div[2]/main/div/div/div[1]/div[1]/div/div[3]/div[5]/a/div/span/span')
    fb_btn.click()
    time.sleep(5)
    # Find and fill in the username and password fields
    username_field = driver.find_element("xpath", '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input')
    username_field.send_keys(username)
    next = driver.find_element("xpath", '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div')
    next.click()
    time.sleep(5)
    password_field = driver.find_element("xpath", '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
    password_field.send_keys(password)

    # Submit the login form
    password_field.send_keys(Keys.RETURN)

    # Wait for the login to complete
    time.sleep(10)


def like_retweet_follow(keyword):
    # Search for a keyword
    search_query = f"{keyword} -filter:retweets -filter:replies filter:images filter:safe"
    driver.get(f"https://twitter.com/search?q=%23{search_query}&src=recent_search_click&f=live")
    time.sleep(10)

    # Extract posts
    likes = driver.find_elements(By.XPATH, "//div[@data-testid='like']")
    retweets = driver.find_elements(By.XPATH, "//div[@data-testid='retweet']")

    print("Found:", len(likes), "posts to like!")
    print("Found:", len(retweets), "posts to retweet!")

    # Like the first post
    if len(likes) > 0:
        driver.execute_script("arguments[0].click();", likes[0])
        print(f"Liked the {keyword} post!")

    # Retweet the first post
    if len(retweets) > 0:
        time.sleep(2)
        driver.execute_script("arguments[0].click();", retweets[0])
        time.sleep(2)
        retweet_menu = driver.find_elements(By.XPATH, "//div[@role='menuitem']")
        retweet_menu[-1].click()
        print(f"Retweeted the {keyword} post!")

# List of keywords to search and interact with
keywords_list = ['CatsOfTwitter', 'DogsOfTwitter', 'Caturday', 'CatsOnTwitter', 'DogsOnTwitter']

# Replace with your Twitter username and password
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
login(username, password)

for keyword in keywords_list:
    like_retweet_follow(keyword)
