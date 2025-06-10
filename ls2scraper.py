import requests




from bs4 import BeautifulSoup


import pandas as pd


import time


import random


import re





# List of User-Agents to rotate


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





def get_product_links(category_url):


    product_links = []


    page = 1


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


        time.sleep(random.uniform(1, 2))  # polite delay


    return product_links





def split_description(full_text):


    split_keyword = "TECHNICAL SPECIFICATIONS"


    if split_keyword in full_text:


        desc, tech = full_text.split(split_keyword, 1)


        return desc.strip(), "TECHNICAL SPECIFICATIONS\n" + tech.strip()


    else:


        return full_text.strip(), None





def extract_helmet_specs(text):


    specs = {}


    # Examples of specs extraction (add more if needed)


    cert = re.findall(r'Certification:\s*([\w\s,.-]+)', text, re.I)


    if cert:


        specs["Certification"] = cert[0].strip()


    shell = re.findall(r'SHELL:\s*(.+)', text, re.I)


    if shell:


        specs["Shell"] = shell[0].strip()


    visor = re.findall(r'VISOR:\s*(.+)', text, re.I)


    if visor:


        specs["Visor"] = visor[0].strip()


    security = re.findall(r'SECURITY:\s*(.+)', text, re.I)


    if security:


        specs["Security Features"] = security[0].strip()


    comfort = re.findall(r'COMFORT:\s*(.+)', text, re.I)


    if comfort:


        specs["Comfort Features"] = comfort[0].strip()


    ventilation = re.findall(r'VENTILATION:\s*(.+)', text, re.I)


    if ventilation:


        specs["Ventilation"] = ventilation[0].strip()


    size_chart = re.findall(r'SIZE CHART:(.+)', text, re.I | re.S)


    if size_chart:


        specs["Size Chart"] = size_chart[0].strip()


    return specs





def scrape_helmet(url):


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


    specs = extract_helmet_specs(tech_text or "")





    return {


        "Product Name": title,


        "Price": price,


        "Description": description,


        "Technical Specifications": tech_text,


        "Image URL": image_url,


        "Product URL": url,


        **specs


    }





def extract_jacket_specs(text):


    specs = {}


    material = re.findall(r'Material\s*:\s*(.+)', text, re.I)


    if material:


        specs["Material"] = material[0].strip()


    protection = re.findall(r'Protection\s*:\s*(.+)', text, re.I)


    if protection:


        specs["Protection"] = protection[0].strip()


    features = re.findall(r'Features\s*:\s*(.+)', text, re.I | re.S)


    if features:


        specs["Features"] = features[0].strip()


    size_chart = re.findall(r'Size Chart\s*:\s*(.+)', text, re.I | re.S)


    if size_chart:


        specs["Size Chart"] = size_chart[0].strip()


    return specs





def scrape_jacket(url):


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


    specs = extract_jacket_specs(tech_text or "")





    return {


        "Product Name": title,


        "Price": price,


        "Description": description,


        "Technical Specifications": tech_text,


        "Image URL": image_url,


        "Product URL": url,


        **specs


    }





def extract_pant_specs(text):


    specs = {}


    material = re.findall(r'Material\s*:\s*(.+)', text, re.I)


    if material:


        specs["Material"] = material[0].strip()


    protection = re.findall(r'Protection\s*:\s*(.+)', text, re.I)


    if protection:


        specs["Protection"] = protection[0].strip()


    features = re.findall(r'Features\s*:\s*(.+)', text, re.I | re.S)


    if features:


        specs["Features"] = features[0].strip()


    size_chart = re.findall(r'Size Chart\s*:\s*(.+)', text, re.I | re.S)


    if size_chart:


        specs["Size Chart"] = size_chart[0].strip()


    return specs





def scrape_pant(url):


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


    specs = extract_pant_specs(tech_text or "")





    return {


        "Product Name": title,


        "Price": price,


        "Description": description,


        "Technical Specifications": tech_text,


        "Image URL": image_url,


        "Product URL": url,


        **specs


    }





def extract_glove_specs(text):


    specs = {}


    material = re.findall(r'Material\s*:\s*(.+)', text, re.I)


    if material:


        specs["Material"] = material[0].strip()


    protection = re.findall(r'Protection\s*:\s*(.+)', text, re.I)


    if protection:


        specs["Protection"] = protection[0].strip()


    features = re.findall(r'Features\s*:\s*(.+)', text, re.I | re.S)


    if features:


        specs["Features"] = features[0].strip()


    size_chart = re.findall(r'Size Chart\s*:\s*(.+)', text, re.I | re.S)


    if size_chart:


        specs["Size Chart"] = size_chart[0].strip()


    return specs





def scrape_glove(url):


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


    specs = extract_glove_specs(tech_text or "")





    return {


        "Product Name": title,


        "Price": price,


        "Description": description,


        "Technical Specifications": tech_text,


        "Image URL": image_url,


        "Product URL": url,


        **specs


    }





if __name__ == "__main__":


    print("🔍 Scraping Helmets (Full Face)...")


    helmet_links = get_product_links("https://ls2helmetsindia.com/product-category/helmets/full-face/")


    helmet_data = [scrape_helmet(url) for url in helmet_links]





    print("🧥 Scraping Jackets...")


    jacket_links = get_product_links("https://ls2helmetsindia.com/product-category/apparel/jackets/")


    jacket_data = [scrape_jacket(url) for url in jacket_links]





    print("👖 Scraping Pants...")


    pant_links = get_product_links("https://ls2helmetsindia.com/shop/?product_cat=pant&filter=1")


    pant_data = [scrape_pant(url) for url in pant_links]





    print("🧤 Scraping Gloves...")


    glove_links = get_product_links("https://ls2helmetsindia.com/product-category/apparel/gloves/")


    glove_data = [scrape_glove(url) for url in glove_links]





    print("📊 Exporting data to Excel...")


    with pd.ExcelWriter("ls2_products_full.xlsx", engine='openpyxl') as writer:


        pd.DataFrame(helmet_data).to_excel(writer, sheet_name="Helmets", index=False)


        pd.DataFrame(jacket_data).to_excel(writer, sheet_name="Jackets", index=False)


        pd.DataFrame(pant_data).to_excel(writer, sheet_name="Pants", index=False)


        pd.DataFrame(glove_data).to_excel(writer, sheet_name="Gloves", index=False)Add commentMore actions





    print("✅ Done! Data saved in ls2_products_full.xlsx")