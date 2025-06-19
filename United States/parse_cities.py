import time
import json
import string
import cloudscraper
from urllib.parse import quote
BASE_URL = "https://www.bbb.org/api/suggest/location?country=USA&input={}&maxMatches=100"

scraper = cloudscraper.create_scraper(
    interpreter="nodejs",
    browser={
        "browser": "chrome",
        "platform": "ios",
        "desktop": False,
    }
)


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "DNT": "1",
    "Pragma": "no-cache",
    "Priority": "u=0, i",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-GPC": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0"
}


# Generate prefixes (A, B, ..., AZ, Ba, ..., etc.)
prefixes = [a for a in string.ascii_uppercase]
results = []
seen = set()

for prefix in prefixes:
    url = BASE_URL.format(quote(prefix))
    try:
        print("trying:", url)
        response = scraper.get(url, headers=headers)
        if response.status_code == 200:
            print(f"✔️ Fetched: {prefix}")
            data = response.json()
            for item in data:
                value = item.get("displayText")
                if value and value not in seen:
                    seen.add(value)
                    results.append(value)
        else:
            print(f"⚠️ Skipped {prefix} - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error on {prefix}: {e}")

    time.sleep(0.2)

# Save to JSON
    with open("us_city_autocomplete.json", "w", encoding="utf-8") as f:
        json.dump(sorted(results), f, ensure_ascii=False, indent=4)

print(f"✅ Saved {len(results)} unique city names to 'us_city_autocomplete.json'")
