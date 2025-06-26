# scraper_multi_xlsx.py
import requests
from bs4 import BeautifulSoup
import re
from openpyxl import Workbook
from urllib.parse import urlparse
from tqdm import tqdm
import sys

BASE_URLS = [
    'https://planetdsg.com/collections/new',
    'https://planetdsg.com/collections/jacket',
    'https://planetdsg.com/collections/gloves',
    'https://planetdsg.com/collections/racing-suits',
    'https://planetdsg.com/collections/pants',
    'https://planetdsg.com/collections/jerseys',
    'https://planetdsg.com/collections/protectors',
    'https://planetdsg.com/collections/technical-apparel',
    'https://planetdsg.com/collections/boots',
    'https://planetdsg.com/collections/accessories',
    'https://planetdsg.com/collections/accessories-1',
    'https://planetdsg.com/collections/sportswear',
    'https://planetdsg.com/collections/dream-street-gear'
]

def clean_price(price_strs):
    for s in price_strs:
        if '₹' in s:
            return re.sub(r'(₹|Regular price|From|On sale from)', '', s).strip()
    return None

def extract_products(soup):
    products = []
    product_items = soup.select('div.collection ul#product-grid li.grid__item')

    for item in product_items:
        card = item.select_one('div.product-card')
        if not card:
            continue

        info_div = card.select_one('div.product-card__info')
        if not info_div:
            continue

        strings = list(info_div.stripped_strings)
        if not strings or len(strings) < 2:
            continue

        name = strings[0]
        price = clean_price(strings[1:])
        if name and price:
            products.append({'name': name, 'price': price})
    return products

def fetch_all_products(base_url):
    all_products = []
    page = 1

    while True:
        url = base_url if page == 1 else f"{base_url}?page={page}"
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        products = extract_products(soup)

        if not products:
            break

        all_products.extend(products)
        page += 1

    return all_products

def get_last_path_segment(url):
    return urlparse(url).path.rstrip('/').split('/')[-1] or "Sheet1"

def save_all_to_excel(base_urls, filename="planetdsg_products.xlsx"):
    wb = Workbook()
    first = True

    print("🚀 Starting scrape and export...\n")
    for url in tqdm(base_urls, file=sys.stdout, desc="Scraping Collections", ncols=80, colour="green"):
        try:
            products = fetch_all_products(url)
            sheet_name = get_last_path_segment(url)[:31]

            if first:
                ws = wb.active
                ws.title = sheet_name
                first = False
            else:
                ws = wb.create_sheet(title=sheet_name)

            ws.append(["Product Name", "Price(₹)"])
            for p in products:
                ws.append([p['name'], p['price']])

            print(f"  ✔️  {sheet_name} — {len(products)} products saved")
        except Exception as e:
            print(f"  ❌  Failed to process {url}: {e}")

    wb.save(filename)
    print(f"\n✅ Excel saved as '{filename}'")

if __name__ == '__main__':
    save_all_to_excel(BASE_URLS)
