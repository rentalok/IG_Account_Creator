# account_creator.py
import json
import os
import random
import string
import threading
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

EMAIL_DOMAINS = ["chefalicious.com"]
ACCOUNT_FILE_TXT = "accounts.txt"
ACCOUNT_FILE_JSON = "accounts.json"


def generate_username():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


def generate_password():
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=12))


def get_temp_email():
    session = requests.Session()
    response = session.get("https://api.mail.tm/domains")
    domain = EMAIL_DOMAINS[0]
    local = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{local}@{domain}"


def save_account(username, password, email):
    with open(ACCOUNT_FILE_TXT, "a") as f:
        f.write(f"{username}:{password}:{email}\n")
    account_data = {"username": username, "password": password, "email": email}
    if os.path.exists(ACCOUNT_FILE_JSON):
        with open(ACCOUNT_FILE_JSON, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(account_data)
    with open(ACCOUNT_FILE_JSON, "w") as f:
        json.dump(data, f, indent=2)


def create_account():
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = uc.Chrome(options=options)

    try:
        email = get_temp_email()
        username = generate_username()
        password = generate_password()

        driver.get("https://www.instagram.com/accounts/emailsignup/")
        time.sleep(5)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
        driver.find_element(By.NAME, "fullName").send_keys("Test User")
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(5)

        if "challenge" in driver.current_url:
            print("[!] Captcha or challenge detected, skipping...")
            driver.quit()
            return

        # Birthday page
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "day"))).send_keys("1")
            driver.find_element(By.NAME, "month").send_keys("Jan")
            driver.find_element(By.NAME, "year").send_keys("2000")
            driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        except:
            print("[!] No birthday page.")

        save_account(username, password, email)
        print(f"[✓] Instagram account created: {username}:{password}:{email}")

    except Exception as e:
        print(f"[!] Account creation error: {e}")
    finally:
        driver.quit()


def main():
    threads = []
    for _ in range(5):  # Change this for more concurrent threads
        t = threading.Thread(target=create_account)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
