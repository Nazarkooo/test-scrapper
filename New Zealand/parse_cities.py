import requests
import json
import time
import string

API_URL = "https://ym3nsybcr5ep3mswew326ssec4.appsync-api.ap-southeast-2.amazonaws.com/graphql"
API_KEY = "da2-yishzvyj6vclpd7nxpiiqra4re"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
}

prefixes = [a + b for a in string.ascii_uppercase for b in string.ascii_lowercase]

results = []
seen = set()

for prefix in prefixes:
    print(f"🔍 Trying prefix: {prefix}")

    payload = {
        "operationName": "autocomplete",
        "variables": {"type": "where", "term": prefix},
        "query": """
        query autocomplete($type: String, $term: String) {
          autocomplete(searchType: $type, term: $term) {
            businesses
            categories
            locations
            __typename
          }
        }
        """,
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            data = response.json()
            locations = (
                data.get("data", {}).get("autocomplete", {}).get("locations", [])
            )
            print(f"✔️ Found {len(locations)} results for '{prefix}'")
            for loc in locations:
                if loc not in seen:
                    seen.add(loc)
                    results.append(loc)
        else:
            print(f"⚠️ Skipped '{prefix}' - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error for prefix '{prefix}': {e}")

    time.sleep(0.2)

# Save to JSON
with open("yellow_au_city_autocomplete.json", "w", encoding="utf-8") as f:
    json.dump(sorted(results), f, ensure_ascii=False, indent=2)

print(
    f"\n✅ Saved {len(results)} unique city names to 'yellow_au_city_autocomplete.json'"
)
