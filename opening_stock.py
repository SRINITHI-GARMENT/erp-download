import os
import time
import smtplib
from datetime import datetime
from email.message import EmailMessage

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# GitHub Secrets
USERNAME = os.environ["ERP_USERNAME"]
PASSWORD = os.environ["ERP_PASSWORD"]

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
EMAIL_TO = os.environ["EMAIL_TO"]

# Download Folder
download_folder = os.path.join(os.getcwd(), "downloads")
os.makedirs(download_folder, exist_ok=True)

# Chrome Options
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

prefs = {
    "download.prompt_for_download": False,
    "download.default_directory": download_folder,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)

# Allow Downloads in Headless Chrome
driver.execute_cdp_cmd(
    "Page.setDownloadBehavior",
    {
        "behavior": "allow",
        "downloadPath": download_folder
    }
)

wait = WebDriverWait(driver, 30)

try:

    print("Opening login page...")

    driver.get("https://erp.datserp.com/#/login")

    email_box = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[ng-model='form.email']")
        )
    )
    email_box.send_keys(USERNAME)

    password_box = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[ng-model='form.password']")
        )
    )
    password_box.send_keys(PASSWORD)

    login_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(.,'Login')]")
        )
    )

    login_btn.click()

    print("Login successful")

    time.sleep