import time
from selenium.webdriver.common.by import By

def long_scroll(driver):
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
    last_height = new_height


def log_in(driver):
    file_path = 'credentials.txt'
    file1 = open(file_path, 'r')
    content = file1.read()

    content = content.split('\n')
    email, password = content[0], content[1]

    button = driver.find_element(By.NAME, 'email')
    button.send_keys(email)

    button = driver.find_element(By.NAME, 'password')
    button.send_keys(password)

    button = driver.find_element(By.NAME, 'auth-login-button')
    button.click()