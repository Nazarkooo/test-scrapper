import json
import re
import sys
from urllib.parse import quote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
import time
# Your constants
PAGE_COUNT = 10
WAIT_TIMEOUT = 10
BASE_URL = "https://www.yellowpages.com.au/search/listings?clue=Roofing+Contractors&locationClue={town}&pageNumber={page}"

RESULT_FILE = "aus_results.json"

INPUT_JSON = "aus_city_autocomplete.json"


try:
    with open(RESULT_FILE, "r", encoding="utf-8") as f:
        results_by_town = json.load(f)
except FileNotFoundError:
    results_by_town = {}

try:
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        towns = json.load(f)
except:
    sys.exit("we need json array to work, start city scrapping")


for town in towns:
    current_count = 0
    max_count = 0

    if town not in results_by_town:
        results_by_town[town] = {}

    print(f"\n📍 Scraping town: {town}")

    for page_num in range(1, PAGE_COUNT + 1):


        if max_count and current_count >= max_count:
            break
        # main cycle

        if str(page_num) in results_by_town[town]:
            print(f"  - Page {page_num} already scraped, skipping")
            continue

        url = BASE_URL.format(town=quote_plus(town), page=page_num)
        print(f"  🔄 Page {page_num}: {url}")

        driver = Driver(uc=True)
        driver.get(url)
        driver.uc_gui_click_captcha()
        wait = WebDriverWait(driver, WAIT_TIMEOUT)


        #here
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'More info')]")))
            more_info_buttons = driver.find_elements(By.XPATH, "//div[contains(text(), 'More info')]")
            results = []

            if not max_count:
                h2 = driver.find_element(By.XPATH, '//h2[contains(text(), "Results for")]')

                match = re.search(r"(\d+)\s+Results", h2.text)
                max_count = int(match.group(1)) if match else 0
                print(max_count)

            print(f"🔎 Found {len(more_info_buttons)} 'More info' elements.")

            for i, btn in enumerate(more_info_buttons):
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(0.2)
                    btn.click()
                    print(f"✅ Clicked 'More info' #{i+1}")
                except Exception as e:
                    pass

            listings = driver.find_elements(By.XPATH, "//*[contains(@class, 'PaidListing') or contains(@class, 'FreeListing')]")
            current_count += len(listings)
            print(f"🔎 Found {len(listings)} listings")

            for list in listings:

                try:
                    name = list.find_element(By.TAG_NAME, "h3").text.strip()
                except:
                    name = "N/A"

                try:
                    try:
                        link = list.find_elements(By.CSS_SELECTOR, "a[href^='https']")[1]
                        address = link.text.strip()
                    except:
                        full_text = list.find_element(By.XPATH, ".//h3/following::p[1]").text
                        address = ','.join(full_text.split(',')[1:]).strip()

                except:
                    address = "N/A"



                try:
                    phone = list.find_element(By.CLASS_NAME, "fXPEMO").text
                        
                except:
                    phone = "N/A"

                results.append({
                    "name": name,
                    "address": address,
                    "phone": phone
                })

                print(f"✅ {name} | {address} | {phone}")

            results_by_town[town][str(page_num)] = results

            # Save after each page
            with open(RESULT_FILE, "w", encoding="utf-8") as f:
                json.dump(results_by_town, f, indent=2, ensure_ascii=False)

            print(f"  ✅ Saved {len(results)} results for page {page_num}")

        except Exception as e:
            print(f"⚠️ Error extracting cards on page {page_num}: {e}")
        finally:
            driver.quit()
