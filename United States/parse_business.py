import json
import sys
from urllib.parse import quote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome as Driver

# Your constants
PAGE_COUNT = 10
WAIT_TIMEOUT = 10
BASE_URL = "https://www.bbb.org/search?find_country=USA&find_text=roofing+contractors&find_loc={town}&page={page}"
RESULT_FILE = "bbb_results.json"
INPUT_JSON = "us_city_autocomplete.json"
# Load existing results if any
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
        wait = WebDriverWait(driver, WAIT_TIMEOUT)

        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-card")))
            cards = driver.find_elements(By.CLASS_NAME, "result-card")
            results = []

            for card in cards:
                try:
                    name = card.find_element(
                        By.CSS_SELECTOR, "h3.result-business-name span"
                    ).text.strip()
                    if name == "advertisement:":
                        continue
                except:
                    name = "N/A"

                try:
                    info_block = card.find_element(
                        By.CLASS_NAME, "result-business-info"
                    )
                except:
                    info_block = None

                try:
                    phone = (
                        info_block.find_element(
                            By.CSS_SELECTOR, 'a[href^="tel:"]'
                        ).text.strip()
                        if info_block
                        else "N/A"
                    )
                except:
                    phone = "N/A"

                try:
                    address = (
                        info_block.find_element(By.CSS_SELECTOR, "p")
                        .text.strip()
                        .replace("\n", " ")
                        if info_block
                        else "N/A"
                    )
                except:
                    address = "N/A"

                results.append({"name": name, "phone": phone, "address": address})

            results_by_town[town][str(page_num)] = results

            # Save after each page
            with open(RESULT_FILE, "w", encoding="utf-8") as f:
                json.dump(results_by_town, f, indent=2, ensure_ascii=False)

            print(f"  ✅ Saved {len(results)} results for page {page_num}")

        except Exception as e:
            print(f"⚠️ Error extracting cards on page {page_num}: {e}")
        finally:
            driver.quit()
