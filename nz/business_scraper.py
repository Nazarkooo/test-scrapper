from seleniumbase import Driver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
from urllib.parse import quote_plus

WAIT_TIMEOUT = 15
PAGE_COUNT = 20
INPUT_JSON = "nz_city_autocomplete.json"
OUTPUT_JSON = "nz_results.json"
BASE_URL = "https://yellow.co.nz/Rock%20And%20Pillar/Roofing%20Contractors/page/{page}?what=Roofing+Contractors&where={town}"

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

            url = BASE_URL.format(town=quote_plus(town), page=page_num)
            print(f"  🔄 Page {page_num}: {url}")

            driver = Driver(uc=True)
            driver.get(url)
            driver.uc_gui_click_captcha()
            wait = WebDriverWait(driver, WAIT_TIMEOUT)

            try:

                try:
                    h4 = driver.find_element(
                        By.XPATH,
                        '//h4[starts-with(text(), "We didn\'t find any businesses matching")]',
                    )
                    print(
                        "❌ No more listings found, stopping pagination for this town."
                    )
                    break
                except:
                    pass
                # Wait for the main column container to appear
                container = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[contains(@class, 'flex flex-col') and contains(@class, 'gap-4') and contains(@class, 'mt-4') and contains(@class, 'animate-fade') and contains(@class, 'block')]",
                        )
                    )
                )

                # Get all business listing divs inside the container
                listings = container.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'flex') and contains(@class, 'gap-4') and contains(@class, 'w-full')]",
                )
                print(f"🔎 Found {len(listings)} business listings.")

                page_results = []

                for idx, listing in enumerate(listings):
                    try:
                        name = listing.find_element(By.TAG_NAME, "h1").text.strip()
                    except:
                        name = "N/A"

                    # Try to reveal and get phone
                    try:
                        phone_button = listing.find_element(
                            By.XPATH, ".//button[.//span[contains(text(), 'Phone')]]"
                        )
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});",
                            phone_button,
                        )
                        time.sleep(0.2)
                        phone_button.click()
                        time.sleep(0.5)  # Let the dropdown show
                        phone_element = listing.find_element(
                            By.XPATH, ".//a[starts-with(@href, 'tel:')]"
                        )
                        phone = phone_element.text.strip()
                    except:
                        phone = "N/A"

                    # Try to extract address
                    try:
                        address = (
                            listing.find_element(
                                By.XPATH, ".//span[@itemprop='address']"
                            )
                            .text.replace("\n", " ")
                            .strip()
                        )

                    except:
                        address = "N/A"

                    print(f"✅ {name} | {address} | {phone}")
                    entry = {"name": name, "address": address, "phone": phone}
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
