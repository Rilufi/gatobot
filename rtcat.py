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
options = Options()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument('--headless')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.binary_location = "/usr/bin/chromium-browser"
driver = webdriver.Chrome(options=options)

def login(username, password, email):
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

    # Check for a second identification page
    try:
        second_identification_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@data-testid='ocfEnterTextTextInput']"))
        )
        # You can handle the second identification here
        print("Second identification page found. Handle it here.")
        # For example, you can fill in the input and submit
        second_identification_input.send_keys(email)
        second_identification_input.send_keys(Keys.RETURN)
        # Wait for the login to complete
        time.sleep(10)
    except TimeoutException:
        # No second identification page, continue with the script
        print("No second identification page found. Continue with the script.")

def like_retweet_follow(keyword):
    print(f"Iniciando interação com a hashtag: {keyword}")
    # Search for a keyword
    search_query = f"{keyword} -filter:retweets -filter:replies filter:images filter:safe"
    driver.get(f"https://twitter.com/search?q=%23{search_query}&src=recent_search_click&f=live")
    print("Aguardando a página de resultados de pesquisa carregar...")
    
    # Aguardar até que os botões de curtir e retweetar estejam visíveis
    try:
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@data-testid='like']"))
        )
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@data-testid='retweet']"))
        )
        print("Página de resultados de pesquisa carregada com sucesso.")
    except TimeoutException:
        print("Tempo de espera excedido. Os resultados da pesquisa podem não ter carregado corretamente.")

    # Extract posts
    likes = driver.find_elements(By.XPATH, "//div[@data-testid='like']")
    retweets = driver.find_elements(By.XPATH, "//div[@data-testid='retweet']")

    print(f"Found: {len(likes)} posts to like!")
    print(f"Found: {len(retweets)} posts to retweet!")

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
email = os.environ.get("EMAIL")  # Adicione esta linha para obter o email do ambiente

# Adicione o bloco try-except para capturar erros e imprimir detalhes do erro
try:
    login(username, password, email)

    for keyword in keywords_list:
        like_retweet_follow(keyword)

except Exception as e:
    print(f"Erro durante a execução: {e}")
    raise  # Re-levanta a exceção para que você possa ver o rastreamento completo no GitHub Actions
finally:
    driver.quit()
