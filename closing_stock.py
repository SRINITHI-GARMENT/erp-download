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

USERNAME = os.environ["ERP_USERNAME"]
PASSWORD = os.environ["ERP_PASSWORD"]

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
EMAIL_TO = os.environ["EMAIL_TO"]

download_folder = os.path.join(os.getcwd(), "downloads")
os.makedirs(download_folder, exist_ok=True)

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

    time.sleep(8)

    driver.get(
        "https://erp.datserp.com/#/erp/finalgoodsSameColorStockReport"
    )

    print("Waiting report page...")
    time.sleep(15)

    buttons = driver.find_elements(By.TAG_NAME, "button")

    print(f"Found {len(buttons)} buttons")

    if len(buttons) > 6:
        buttons[6].click()
        print("Excel Download Triggered")
    else:
        raise Exception("Excel button not found")

    time.sleep(10)

    downloaded_file = None

    print("Checking download folder...")

    for _ in range(90):

        files = os.listdir(download_folder)

        for file in files:

            print("Found:", file)

            if (
                file.endswith(".xlsx")
                or file.endswith(".xls")
                or file.endswith(".csv")
            ):
                downloaded_file = os.path.join(
                    download_folder,
                    file
                )
                break

        if downloaded_file:
            break

        time.sleep(2)

    if not downloaded_file:

        print("Current URL:")
        print(driver.current_url)

        print("Download folder:")
        print(download_folder)

        print("Files:")
        print(os.listdir(download_folder))

        driver.save_screenshot("download_error.png")

        raise Exception("Downloaded file not found")

    today = datetime.now().strftime("%Y-%m-%d")

    ext = os.path.splitext(downloaded_file)[1]

    final_file = os.path.join(
        download_folder,
        f"Closing_{today}{ext}"
    )

    os.rename(downloaded_file, final_file)

    print("File renamed:")
    print(final_file)

    msg = EmailMessage()

    msg["Subject"] = f"Closing Stock Report - {today}"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    msg.set_content(
        f"Closing Stock Report attached.\nDate: {today}"
    )

    with open(final_file, "rb") as f:

        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename=os.path.basename(final_file)
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

        smtp.login(
            EMAIL_USER,
            EMAIL_PASS
        )

        smtp.send_message(msg)

    print("Email Sent Successfully")

except Exception as e:

    print("ERROR:")
    print(str(e))

    driver.save_screenshot("error.png")

finally:

    driver.quit()