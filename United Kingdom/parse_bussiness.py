from seleniumbase import Driver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os

WAIT_TIMEOUT = 15
PAGE_COUNT = 20
INPUT_JSON = "yell_uk_city_autocomplete.json"
OUTPUT_JSON = "yell_roofers_by_town.json"
BASE_URL = "https://www.yell.com/ucs/UcsSearchAction.do?keywords=Roofing&location={town}&pageNum={page}"

# Load towns (expects list of town strings)
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    towns = json.load(f)

results_by_town = {}

# Load existing results if file exists (to resume)
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        results_by_town = json.load(f)

try:
    for town in towns:
        if town not in results_by_town:
            results_by_town[town] = {}

        print(f"\n📍 Scraping town: {town}")

        for page_num in range(1, PAGE_COUNT + 1):
            if str(page_num) in results_by_town[town]:
                print(f"  - Page {page_num} already scraped, skipping")
                continue

            url = BASE_URL.format(town=town.replace(" ", "+"), page=page_num)
            print(f"  🔄 Page {page_num}: {url}")

            driver = Driver(uc=True)
            driver.get(url)
            driver.uc_gui_click_captcha()
            wait = WebDriverWait(driver, WAIT_TIMEOUT)

            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "businessCapsule--mainRow")))
                listings = driver.find_elements(By.CLASS_NAME, "businessCapsule--mainRow")

                page_results = []
                seen_addresses = set()

                for listing in listings:
                    try:
                        name = listing.find_element(By.CSS_SELECTOR, "h2").text.strip()
                    except:
                        name = "N/A"

                    # Reveal phone(s)
                    try:
                        phone_label = listing.find_element(By.CSS_SELECTOR, "label.business--telephone")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_label)
                        time.sleep(0.3)
                        phone_label.click()
                        time.sleep(1)
                    except:
                        pass

                    try:
                        phones_wrapper = listing.find_element(By.CLASS_NAME, "business--multiplePhonesWrapper")
                        phone_spans = phones_wrapper.find_elements(By.CLASS_NAME, "business--telephoneNumber")
                        phone = ", ".join([span.text.strip() for span in phone_spans])
                    except:
                        phone = "N/A"

                    try:
                        address_root = listing.find_element(By.CSS_SELECTOR, '[itemprop="address"]')
                        street = address_root.find_element(By.CSS_SELECTOR, '[itemprop="streetAddress"]').text.strip()
                        city = address_root.find_element(By.CSS_SELECTOR, '[itemprop="addressLocality"]').text.strip()
                        postal = address_root.find_element(By.CSS_SELECTOR, '[itemprop="postalCode"]').text.strip()
                        address = f"{street} {city}, {postal}"
                    except:
                        address = "N/A"

                    if address in seen_addresses:
                        continue
                    seen_addresses.add(address)

                    entry = {
                        "name": name,
                        "address": address,
                        "phone": phone
                    }
                    page_results.append(entry)

                results_by_town[town][str(page_num)] = page_results

                # Save results after each page
                with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                    json.dump(results_by_town, f, ensure_ascii=False, indent=4)

            except Exception as e:
                print(f"    ⚠️ Page {page_num} failed: {e}")
                results_by_town[town][str(page_num)] = []
                break

            finally:
                driver.quit()
                time.sleep(1)

finally:
    print("\n✅ Scraping complete.")
