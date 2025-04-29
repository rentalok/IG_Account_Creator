import requests
import uuid
import time
import threading
import random
import string
import json
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SAVE_FILE_TXT = "accounts.txt"
SAVE_FILE_JSON = "accounts.json"
PROXY_API = "https://www.proxy-list.download/api/v1/get?type=https"

def get_random_proxy():
    try:
        proxies = requests.get(PROXY_API).text.strip().split("\r\n")
        return random.choice(proxies)
    except:
        return None

def get_temp_email():
    session = requests.Session()
    try:
        domain_resp = session.get('https://api.mail.tm/domains')
        domain_resp.raise_for_status()
        domain = domain_resp.json()['hydra:member'][0]['domain']

        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        password = "Password123!"
        email_address = f"{username}@{domain}"

        account_data = {
            "address": email_address,
            "password": password
        }

        create_resp = session.post('https://api.mail.tm/accounts', json=account_data)
        if create_resp.status_code != 201:
            return get_temp_email()

        token_resp = session.post('https://api.mail.tm/token', json=account_data)
        token_resp.raise_for_status()
        token = token_resp.json()['token']

        return {
            'email': email_address,
            'password': password,
            'token': token
        }
    except:
        return get_temp_email()

def random_username():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=12))

def save_account(username, password, email):
    with open(SAVE_FILE_TXT, "a") as f:
        f.write(f"{username}:{password}:{email}\n")
    if os.path.exists(SAVE_FILE_JSON):
        with open(SAVE_FILE_JSON, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append({"username": username, "password": password, "email": email})
    with open(SAVE_FILE_JSON, "w") as f:
        json.dump(data, f, indent=4)

def create_instagram_account():
    try:
        email_data = get_temp_email()
        email = email_data['email']
        password = random_password()
        username = random_username()
        full_name = " ".join(["".join(random.choices(string.ascii_letters, k=random.randint(3, 7))) for _ in range(2)])

        proxy = get_random_proxy()
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')

        if proxy:
            options.add_argument(f'--proxy-server=http://{proxy}')

        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 20)

        driver.get("https://www.instagram.com/accounts/emailsignup/")
        time.sleep(2)

        wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
        driver.find_element(By.NAME, "fullName").send_keys(full_name)
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)

        signup_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        if not signup_btn.is_enabled():
            print("[!] Captcha or bot detection triggered. Skipping...")
            driver.quit()
            return

        signup_btn.click()
        print(f"[+] Submitted signup for {username}")

        time.sleep(5)
        try:
            wait.until(EC.presence_of_element_located((By.NAME, "day"))).send_keys(str(random.randint(1, 28)))
            driver.find_element(By.NAME, "month").send_keys(str(random.randint(1, 12)))
            driver.find_element(By.NAME, "year").send_keys(str(random.randint(1995, 2001)))
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
        except:
            print("[!] Birthday page skipped or auto-filled.")

        time.sleep(5)
        save_account(username, password, email)
        print(f"[✓] Created IG account: {username}:{password}:{email}")
        driver.quit()
    except Exception as e:
        print(f"[!] Error: {e}")

def worker():
    while True:
        create_instagram_account()
        time.sleep(random.randint(10, 20))

if __name__ == "__main__":
    threads = 3  # Adjust for Railway's free limits
    for _ in range(threads):
        threading.Thread(target=worker, daemon=True).start()
    while True:
        time.sleep(100)
