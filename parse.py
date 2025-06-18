import cloudscraper
import requests
from bs4 import BeautifulSoup
from models import Company
from database_utils import use_db, save_company_to_db
import re
import json


BBB_URL = "https://www.bbb.org"

#find_country = ["US", "CAN"]

headers_initial = {
    "Accept": "application/json, text/plain, */*", 
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "DNT": "1",
    "Host": "www.bbb.org",
    "Sec-GPC": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0",
    "Referer": "https://www.bbb.org/search",
    "Origin": "https://www.bbb.org",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

BASE_URL = "https://www.bbb.org"

headers_extra = {
    "Host": "www.bbb.org",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, zstd",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i"
}

scraper = cloudscraper.create_scraper(
    interpreter="nodejs",
    browser={
        "browser": "chrome",
        "platform": "ios",
        "desktop": False,
    }
)



test_url = "https://www.bbb.org/us/ny/new-york/profile/restaurants/taam-tov-restaurant-inc-0121-170777"


def fetch_initial_info(param_text, page_number, country, city):
    

    params = {
    "find_text": {param_text},
    "find_country": country,
    "page": {str(page_number)},
    "find_loc": city
    }

    FETCH_URL = BASE_URL + "/api/search"
    #testing
    req = requests.Request("GET", FETCH_URL, params=params, headers=headers_initial)
    prepared = req.prepare()
    print("Full link:", prepared.url) 

    response = scraper.get(FETCH_URL, headers=headers_initial, params=params)
    if response.status_code // 100 == 2 :
        data = response.json()
        
        results = data["results"]

        for item in results:
            company = Company(
                company_id=item["id"],
                category=item["tobText"],
                brand = re.sub(r"</?em>", "",item["businessName"]),
                phone=item["phone"],
                address=item["address"],
                city=item["city"],
                state=item["state"],
                postalCode=item["postalcode"],
                reportUrl=item["localReportUrl"],
                owner = None
            )
            fetch_extra_info(company)

            use_db(
                dbname="bbb",
                user="postgres",
                password="1234",
                callback=lambda cursor, conn: save_company_to_db(cursor, company)
            )

    else:
        print("Problem with response:", response.status_code)
        print(response.text)


def fetch_extra_info(company : Company):

    if not company.reportUrl:
        return
    
    FETCH_URL = BASE_URL + company.reportUrl

    response = scraper.get(FETCH_URL, headers=headers_extra)


    if response.status_code // 100 != 2:
        print(f"Failed to fetch extra info for {company.brand}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    website_link_tag = soup.select_one("a:-soup-contains('Visit Website')")
    website_url = website_link_tag["href"] if website_link_tag else None
    print(website_url)

    years_tag = soup.select_one("p:-soup-contains('Years in Business')")
    years = years_tag.text.split(":")[-1].strip() if years_tag else None
    print(years)

    description_heading = soup.find("h2", id="about")
    description_body_div = description_heading.find_next_sibling("div", class_="bds-body") if description_heading else None
    description = description_body_div.text.strip() if description_body_div else None

    print(description)

    possible_names = ["Owner", "Director", "President"]

    owners_tag = []
    # slow 
    for dd in soup.select("dd"):
        if any(name in dd.get_text() for name in possible_names):
            owners_tag.append(dd)
    if owners_tag: company.owner = str(owners_tag[0])
    
country_name =  ["USA", "CAN"]
response = scraper.get("https://www.bbb.org/api/suggest/location?country=USA&input=a&maxMatches=50")
city_name = [el['displayText'] for el in response.json()]

for country in country_name:
    for city in city_name:
        fetch_initial_info("Roofing",2,country,city)