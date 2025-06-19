import requests
import json
import string
import time

BASE_URL = "https://www.yellowpages.ca/tools/ac/where/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.yellowpages.ca/",
    "DNT": "1",
    "Connection": "keep-alive",
}

seen = set()
results = []

# Generate prefixes to try (you can extend this to 3-letter combos if needed)
prefixes = list(string.ascii_uppercase) + [
    a + b for a in string.ascii_uppercase for b in string.ascii_lowercase
]

for prefix in prefixes:
    url = BASE_URL + prefix
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"Trying {prefix}")
            data = response.json()
            suggestions = data.get("suggestedValues", [])
            for item in suggestions:
                value = item.get("value")
                if value and value not in seen:
                    seen.add(value)
                    results.append(value)
        else:
            print(f"Skipped {prefix} - HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching {prefix}: {e}")

    time.sleep(0.2)  # Be gentle with server

# Save results
with open("canadian_cities_autocomplete.json", "w", encoding="utf-8") as f:
    json.dump(sorted(results), f, ensure_ascii=False, indent=4)

print(f"Saved {len(results)} unique city names.")
