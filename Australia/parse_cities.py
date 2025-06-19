import string
from urllib.parse import quote
import cloudscraper
from bs4 import BeautifulSoup
import json

API_URL = "https://www.yellowpages.com.au/autosuggest/where?term={}"
OUTPUT_FILE = "aus_city_autocomplete.json"

scraper = cloudscraper.create_scraper(
    interpreter="nodejs",
    browser={
        "browser": "chrome",
        "platform": "ios",
        "desktop": False,
    }
)


headers = {
    "Host": "www.yellowpages.com.au",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "DNT": "1",
    "Priority": "u=0, i",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}


prefixes = [a + b for a in string.ascii_uppercase for b in string.ascii_lowercase]

results = []
seen = set()

for prefix in prefixes:
    url = API_URL.format(quote(prefix))
    print(f"\n🔎 Scraping prefix: {prefix}")

    try:
        response = scraper.get(url, headers=headers)

        if response.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            addresses = [li.text.strip() for li in soup.select("ul.suggestions li")]

            new_items = 0
            for addr in addresses:
                if addr not in seen:
                    seen.add(addr)
                    results.append(addr)
                    new_items += 1

            print(f"✅ Found {len(addresses)} items ({new_items} new)")
        else:
            print(f"❌ Failed HTTP {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error on prefix {prefix}: {e}")

# Save unique results sorted
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(sorted(results), f, ensure_ascii=False, indent=2)

print(f"\n✅ Finished! Saved {len(results)} unique addresses to '{OUTPUT_FILE}'")