from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os

# === CONFIG ===
PAGE_COUNT = 3  # pages per city (can increase later)
INPUT_JSON = "../canada/canadian_cities_autocomplete.json"
OUTPUT_JSON = "roofing_businesses_by_city.json"
WAIT_TIMEOUT = 15

# === SETUP SELENIUM ===
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, WAIT_TIMEOUT)

# === LOAD LOCATIONS ===
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    city_names = json.load(f)

results_by_city = {}
seen_addresses = set()

try:
    for city in city_names:
        city_results = {}

        print(f"\n📍 Scraping city: {city}")
        location = city.replace(" ", "+")  # URL encode like "Toronto, ON" → "Toronto-ON"
        
        for i in range(1, PAGE_COUNT + 1):
            BASE_URL = f"https://www.yellowpages.ca/search/si/{i}/Roofing/{location}"
            print(f"  🔄 Page {i}: {BASE_URL}")
            driver.get(BASE_URL)

            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing")))
            except:
                print("   ⚠️ No listings found.")
                continue

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

            city_results[str(i)] = page_results

        results_by_city[city] = city_results

        # Save after each city
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(results_by_city, f, ensure_ascii=False, indent=4)

finally:
    driver.quit()
    print("\n✅ Scraping complete.")
