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

prefs = {
    "download.prompt_for_download": False,
    "download.default_directory": download_folder,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

try:
    print("Opening login page...")

    driver.get("https://erp.datserp.com/#/login")

    # Email
    email_box = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[ng-model='form.email']")
        )
    )
    email_box.send_keys(USERNAME)

    # Password
    password_box = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[ng-model='form.password']")
        )
    )
    password_box.send_keys(PASSWORD)

    # Login
    login_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(.,'Login')]")
        )
    )

    login_btn.click()

    print("Login successful")

    time.sleep(8)

    # Report Page
    driver.get(
        "https://erp.datserp.com/#/erp/finalgoodsSameColorStockReport"
    )

    print("Waiting report page...")
    time.sleep(15)

    buttons = driver.find_elements(By.TAG_NAME, "button")

    if len(buttons) > 6:
        buttons[6].click()
        print("Excel Download Triggered")
    else:
        raise Exception("Excel button not found")

    # Wait for Download
    time.sleep(20)

    downloaded_file = None

    for file in os.listdir(download_folder):
        if file.endswith(".xlsx"):
            downloaded_file = os.path.join(download_folder, file)
            break

    if not downloaded_file:
        raise Exception("Downloaded file not found")

    # Rename File
    today = datetime.now().strftime("%Y-%m-%d")

    final_file = os.path.join(
        download_folder,
        f"Opening_{today}.xlsx"
    )

    os.rename(downloaded_file, final_file)

    print(f"Renamed to {final_file}")

    # Send Email
    msg = EmailMessage()

    msg["Subject"] = f"Opening Stock Report - {today}"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    msg.set_content(
        f"Opening Stock Report attached.\n\nDate: {today}"
    )

    with open(final_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=os.path.basename(final_file)
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

    print("Email Sent Successfully")

except Exception as e:
    print("ERROR:")
    print(str(e))
    driver.save_screenshot("error.png")

finally:
    driver.quit()