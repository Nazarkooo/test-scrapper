from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import json



options = Options()
options.add_argument("--start-maximized")


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)


page_count = 20
results_by_page = {}
seen_addresses = set()

try:
    for i in range(1, page_count + 1):
        BASE_URL = f"https://www.yellowpages.ca/search/si/{i}/Roofing/Canada"
        print(f"Processing page {i}: {BASE_URL}")
        driver.get(BASE_URL)

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing")))

        listings = driver.find_elements(By.CLASS_NAME, "listing")
        page_results = []

        for listing in listings:
            try:
                name = listing.find_element(By.CSS_SELECTOR, "h3 a.listing__name--link").text.strip()
            except:
                name = "N/A"

            try:
                address_div = listing.find_element(By.CLASS_NAME, "listing__address--full")
                address = address_div.text.strip().replace('\n', ', ')
            except:
                address = "N/A"

            if address in seen_addresses:
                continue

            try:
                phone_button = listing.find_element(By.CSS_SELECTOR, "li.mlr__item--phone a.jsMlrMenu")
                driver.execute_script("arguments[0].click();", phone_button)
                time.sleep(0.5)
                phone = listing.find_element(By.CSS_SELECTOR, ".mlr__submenu__item h4").text.strip()
            except:
                phone = "N/A"

            entry = {
                "name": name,
                "address": address,
                "phone": phone
            }
            page_results.append(entry)
            seen_addresses.add(address)

        results_by_page[str(i)] = page_results  # Store results by page as string keys

        # Save updated results_by_page after each page
        with open("roofing_businesses.json", "w", encoding="utf-8") as f:
            json.dump(results_by_page, f, ensure_ascii=False, indent=4)

finally:
    driver.quit()
