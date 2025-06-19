# 🌍 Roofing Business Scraper

This project scrapes roofing contractor business data — including **company names**, **phone numbers**, and **addresses** — from online directories across **the US, UK, Canada, Australia, and New Zealand**.

The output is saved in structured `.json` files, organized by country and city.

---

## 📦 Features

- ✅ Scrapes roofing contractors by city
- ✅ Handles 5 countries: US, UK, CA, AUS, NZ
- ✅ Collects: name, phone number, address
- ✅ Saves results per city in JSON
- ✅ Can resume progress (saves after each page)
- ✅ Includes city name autocomplete scraping
- ✅ Automatically bypasses Cloudflare protection
- ✅ Error-tolerant with fallback logic

---

## 🗂 Project Structure

Each country has its own folder with:

- `city_scraper.py` – collects city names or location suggestions
- `business_scraper.py` – scrapes business listings using city list
- Output: one or more JSON files per country

Example:
```
project_root/
│
├── us/
│   ├── city_scraper.py
│   ├── business_scraper.py
│   └── us_results.json
│
├── uk/
│   └── ...
├── ca/
├── au/
├── nz/
│
├── requirements.txt
└── README.md
```

---

## 🛠 How to Run

1. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**

   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **Unix/macOS**:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Navigate to the target country folder:**

   ```bash
   cd uk  # or us, ca, au, nz
   ```

5. **Run the city scraper first:**

   ```bash
   python city_scraper.py
   ```

   Wait for it to finish. It will generate a `*_city_autocomplete.json` file.

6. **Run the business scraper next:**

   ```bash
   python business_scraper.py
   ```

   You can interrupt this script at any time — it saves results after scraping each page.

---

## 💾 Output Format

Each result file is a dictionary keyed by city name and page number, for example:

```json
{
  "Los Angeles, CA": {
    "1": [
      {
        "name": "Best Roofing Inc.",
        "address": "1234 Sunset Blvd, Los Angeles, CA 90026",
        "phone": "123-456-7890"
      }
    ]
  }
}
```

---

## 🧱 Dependencies

- `selenium`
- `seleniumbase`
- `webdriver-manager`
- `requests`
- `json`, `re`, `time`, `os`, `sys`, etc.

See `requirements.txt` for full list.

---

## ❗ Notes

- Some directories (like AU) require Cloudflare bypassing; handled using `seleniumbase` with `uc=True`.
- Scraping time varies by country — be patient.
- Internet connection and up-to-date Chrome browser required.