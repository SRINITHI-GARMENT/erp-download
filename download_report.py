from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

USERNAME = "jana@sng.com"
PASSWORD = "Jana@#123"

options = Options()

prefs = {
    "download.prompt_for_download": False,
    "download.default_directory": r"C:\ERP_DOWNLOADS",
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
    email_box.clear()
    email_box.send_keys(USERNAME)

    print("Email entered")

    # Password
    password_box = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[ng-model='form.password']")
        )
    )
    password_box.clear()
    password_box.send_keys(PASSWORD)

    print("Password entered")

    # Login
    login_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(.,'Login')]")
        )
    )

    print("Clicking login...")
    login_btn.click()

    time.sleep(8)

    print("Opening report page...")
    driver.get(
        "https://erp.datserp.com/#/erp/finalgoodsSameColorStockReport"
    )

    print("Waiting for report page...")
    time.sleep(15)

    buttons = driver.find_elements(By.TAG_NAME, "button")

    print(f"Found {len(buttons)} buttons")

    for i, btn in enumerate(buttons):
        try:
            print(f"\nButton {i}")
            print(btn.get_attribute("outerHTML")[:300])
        except:
            pass

    # Click GREEN Excel button
    print("\nClicking Green Excel Button...")

    if len(buttons) > 6:
        buttons[6].click()
        print("Green Excel Button Clicked")
    else:
        print("Button 6 not found!")

    time.sleep(15)

    # Save screenshot after click
    driver.save_screenshot("after_excel_click.png")
    print("Screenshot saved: after_excel_click.png")

    # Check downloaded files
    import os

    download_folder = r"C:\ERP_DOWNLOADS"

    if os.path.exists(download_folder):
        files = os.listdir(download_folder)

        print("\nFiles found in download folder:")
        for f in files:
            print(f)

        if not files:
            print("No files downloaded")
    else:
        print("Download folder does not exist")

except Exception as e:
    print("\nERROR:")
    print(str(e))

    print("\nCurrent URL:")
    print(driver.current_url)

    driver.save_screenshot("error.png")
    print("Screenshot saved as error.png")

finally:
    input("\nPress Enter to close browser...")
    driver.quit()