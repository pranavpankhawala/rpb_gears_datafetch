import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import logging
from tqdm import tqdm

# -----------------------------
# Setup Logging
# -----------------------------
logging.basicConfig(
    filename="scrape.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# -----------------------------
# User Agents
# -----------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Mobile Safari/537.36",
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

# -----------------------------
# Fetch Product Links with Progress
# -----------------------------
def get_product_links(category_url):
    product_links = []
    page = 1
    with tqdm(desc="Fetching pages", unit=" page") as pbar:
        while True:
            if "?" in category_url:
                url = f"{category_url}&paged={page}"
            else:
                url = f"{category_url}page/{page}/"
            response = requests.get(url, headers=get_headers())
            soup = BeautifulSoup(response.text, "html.parser")
            product_cards = soup.select("ul.products li.product a.woocommerce-LoopProduct-link")
            if not product_cards:
                break
            new_links_found = False
            for card in product_cards:
                href = card.get("href")
                if href and href not in product_links:
                    product_links.append(href)
                    new_links_found = True
            if not new_links_found:
                break
            page += 1
            pbar.update(1)
            time.sleep(random.uniform(1, 2))
    return product_links

# -----------------------------
# Shared Description Splitter
# -----------------------------
def split_description(full_text):
    split_keyword = "TECHNICAL SPECIFICATIONS"
    if split_keyword in full_text:
        desc, tech = full_text.split(split_keyword, 1)
        return desc.strip(), "TECHNICAL SPECIFICATIONS\n" + tech.strip()
    else:
        return full_text.strip(), None

# -----------------------------
# Spec Extractors
# -----------------------------
def extract_helmet_specs(text):
    specs = {}
    cert = re.findall(r"Certification:\s*([\w\s,.-]+)", text, re.I)
    if cert: specs["Certification"] = cert[0].strip()
    shell = re.findall(r"SHELL:\s*(.+)", text, re.I)
    if shell: specs["Shell"] = shell[0].strip()
    visor = re.findall(r"VISOR:\s*(.+)", text, re.I)
    if visor: specs["Visor"] = visor[0].strip()
    security = re.findall(r"SECURITY:\s*(.+)", text, re.I)
    if security: specs["Security Features"] = security[0].strip()
    comfort = re.findall(r"COMFORT:\s*(.+)", text, re.I)
    if comfort: specs["Comfort Features"] = comfort[0].strip()
    ventilation = re.findall(r"VENTILATION:\s*(.+)", text, re.I)
    if ventilation: specs["Ventilation"] = ventilation[0].strip()
    size_chart = re.findall(r"SIZE CHART:(.+)", text, re.I | re.S)
    if size_chart: specs["Size Chart"] = size_chart[0].strip()
    return specs

def extract_jacket_specs(text):
    specs = {}
    material = re.findall(r"Material\s*:\s*(.+)", text, re.I)
    if material: specs["Material"] = material[0].strip()
    protection = re.findall(r"Protection\s*:\s*(.+)", text, re.I)
    if protection: specs["Protection"] = protection[0].strip()
    features = re.findall(r"Features\s*:\s*(.+)", text, re.I | re.S)
    if features: specs["Features"] = features[0].strip()
    size_chart = re.findall(r"Size Chart\s*:\s*(.+)", text, re.I | re.S)
    if size_chart: specs["Size Chart"] = size_chart[0].strip()
    return specs

extract_pant_specs = extract_jacket_specs
extract_glove_specs = extract_jacket_specs

# -----------------------------
# Scrapers for each category
# -----------------------------
def generic_scraper(url, extractor):
    response = requests.get(url, headers=get_headers())
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.select_one("h1.product_title")
    title = title.get_text(strip=True) if title else None
    price = soup.select_one("p.price")
    price = price.get_text(strip=True) if price else None
    desc_raw = soup.select_one("div.woocommerce-Tabs-panel--description")
    desc_raw = desc_raw.get_text("\n", strip=True) if desc_raw else ""
    image_tag = soup.select_one("figure.woocommerce-product-gallery__wrapper img")
    image_url = image_tag["src"] if image_tag else None
    description, tech_text = split_description(desc_raw)
    specs = extractor(tech_text or "")
    return {
        "Product Name": title,
        "Price": price,
        "Description": description,
        "Technical Specifications": tech_text,
        "Image URL": image_url,
        "Product URL": url,
        **specs,
    }

# Category-specific wrappers
def scrape_helmet(url): return generic_scraper(url, extract_helmet_specs)
def scrape_jacket(url): return generic_scraper(url, extract_jacket_specs)
def scrape_pant(url): return generic_scraper(url, extract_pant_specs)
def scrape_glove(url): return generic_scraper(url, extract_glove_specs)

# -----------------------------
# Try-Scrape Helper with Logging
# -----------------------------
def try_scrape(scrape_func, url, label, failed_list, data_list):
    try:
        data_list.append(scrape_func(url))
        logging.info(f"✅ Scraped {label}: {url}")
    except Exception as e:
        print(f"❌ Failed to scrape {label}: {url}")
        logging.error(f"❌ Failed to scrape {label}: {url} — {e}")
        failed_list.append((label, url))

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    failed_urls = []

    categories = [
        ("Helmets", "https://ls2helmetsindia.com/product-category/helmets/full-face/", scrape_helmet),
        ("Jackets", "https://ls2helmetsindia.com/product-category/apparel/jackets/", scrape_jacket),
        ("Pants", "https://ls2helmetsindia.com/shop/?product_cat=pant&filter=1", scrape_pant),
        ("Gloves", "https://ls2helmetsindia.com/product-category/apparel/gloves/", scrape_glove)
    ]

    all_data = {}

    for label, link, scraper in categories:
        print(f"🔍 Scraping {label}...")
        links = get_product_links(link)
        print(f"🔗 Found {len(links)} {label.lower()}.")
        logging.info(f"Found {len(links)} {label.lower()} to scrape.")

        data = []
        for url in tqdm(links, desc=label):
            try_scrape(scraper, url, label, failed_urls, data)
        all_data[label] = data

    # Export to Excel
    print("📊 Exporting data to Excel...")
    with pd.ExcelWriter("ls2_products_full.xlsx", engine="openpyxl") as writer:
        for label, data in all_data.items():
            pd.DataFrame(data).to_excel(writer, sheet_name=label, index=False)
    print("✅ Data saved to ls2_products_full.xlsx")
    logging.info("✅ Data saved to ls2_products_full.xlsx")

    # Retry failed
    if failed_urls:
        print(f"\n🚨 {len(failed_urls)} failed URLs. Retrying...")
        logging.warning(f"{len(failed_urls)} failed URLs on first attempt.")

        retry_failed = []
        label_to_scraper = dict((label, func) for label, _, func in categories)

        for label, url in tqdm(failed_urls, desc="Retrying"):
            try_scrape(label_to_scraper[label], url, label, retry_failed, all_data[label])

        if retry_failed:
            print(f"❌ Still failed after retry: {len(retry_failed)}")
            with open("failed_urls.txt", "w") as f:
                for label, url in retry_failed:
                    f.write(f"{label}: {url}\n")
            print("📄 Failed URLs written to failed_urls.txt")
            logging.error(f"{len(retry_failed)} URLs failed even after retry. Saved to failed_urls.txt")
        else:
            print("🎉 All previously failed URLs scraped successfully on retry!")
            logging.info("🎉 All previously failed URLs scraped successfully on retry!")
    else:
        print("🎉 All products scraped successfully on first attempt!")
