from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
from pyvirtualdisplay import Display
import time
import os

display = Display(visible=0, size=(800, 800))
display.start()

chromedriver_autoinstaller.install()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-size=1200,1200")
chrome_options.add_argument("--ignore-certificate-errors")

driver = webdriver.Chrome(options=chrome_options)

def login(username, password):
    driver.get('https://twitter.com')
    time.sleep(5)

    fb_btn = driver.find_element(By.XPATH, '/html/body/div/div/div/div[2]/main/div/div/div[1]/div[1]/div/div[3]/div[5]/a/div/span/span')
    fb_btn.click()
    time.sleep(5)

    username_field = driver.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input')
    username_field.send_keys(username)
    
    next_button = driver.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div')
    next_button.click()
    time.sleep(5)
    
    password_field = driver.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
    password_field.send_keys(password)

    password_field.send_keys(Keys.RETURN)
    time.sleep(10)

def like_retweet_follow(keyword):
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

    # Like the first post
    if likes:
        likes[0].click()
        print(f"Liked the {keyword} post!")

    # Retweet the first post
    if retweets:
        time.sleep(2)
        retweets[0].click()
        time.sleep(2)
        retweet_menu = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@role='menuitem']")))
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
