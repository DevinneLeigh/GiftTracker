import html
import re
from urllib.parse import urlparse
from django.contrib.auth.models import User
from decimal import Decimal
import requests
from bs4 import BeautifulSoup
import json

def get_default_user():
    user, created = User.objects.get_or_create(
        username="default_user",
        defaults={"password": "!"},  # unusable password
    )
    return user

def compute_totals(participants):
    for p in participants:
        total_spent = sum(Decimal(gift.product_price or 0) for gift in p.gift_set.all())
        budget_amount = Decimal(p.budget.price) if hasattr(p, "budget") and p.budget else Decimal('0')
        p.spent = total_spent
        p.remaining = budget_amount - total_spent
    return participants


def shorten_name(text: str) -> str | None:
    return text.split(",")[0]

def extract_target_price_from_script(script_text: str) -> float | None:
    """
    Extracts the current_retail price from a Target script tag string.
    Returns a float price, or None if not found.
    """
    match = re.search(r'\\"price\\":\{\\"current_retail\\":([\d\.]+)', script_text)
    if match:
        return float(match.group(1))
    return None

def extract_target_short_name(script_text: str) -> float | None:
    match = re.search(r'\\"name\\":\\"([\w ]+)\\"},\\"product_classification\\":', script_text)
    if match:
        return match.group(1)
    return None

def scrape_walmart(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")

    if not script:
        return None  # Bot blocked or unusual page

    data = json.loads(script.string)

    try:
        product = data["props"]["pageProps"]["initialData"]["data"]["product"]

        return {
            "name": product.get("name"),
            "price": product.get("priceInfo", {}).get("currentPrice", {}).get("price"),
            "image": product.get("imageInfo", {}).get("thumbnailUrl"),
        }
    except Exception as e:
        print("Parsing error:", e)
        return None

def extract_amazon_image_from_dynamic_image_attr(attr_value: str) -> str | None:
    """
    Extracts the first image URL from Amazon's 'data-a-dynamic-image' attribute
    when it is HTML-encoded.
    """
    if not attr_value:
        return None

    decoded = html.unescape(attr_value)

    # Capture full quoted URL
    match = re.search(r'"(https://m\.media-amazon\.com[^"]+)"', decoded)
    if match:
        return match.group(1)

    return None

    
def scrape_amazon(url):
    price = None 
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    price_container = soup.find("span", id="tp_price_block_total_price_ww")
    if price_container:
        price_tag = price_container.find("span", class_="a-offscreen")
        if price_tag:
            price = price_tag.get_text(strip=True)

    try:
        return {
            "price": price,
            "soup": soup
        }
    except Exception as e:
        print("Parsing error:", e)
        return None
    

def get_store_from_url(url: str) -> str | None:
    """
    Extracts the naked TLD of a URL, e.g., 'amazon', 'walmart', 'target'.
    Returns None if the domain is not recognized.
    """
    domain = urlparse(url).netloc.lower()
    
    # Remove 'www.' prefix if present
    if domain.startswith("www."):
        domain = domain[4:]
    
    # Take only the part before the first '.'
    naked_domain = domain.split(".")[0]
    
    # Only return if it's one of the known stores
    if naked_domain in ["amazon", "walmart", "target"]:
        return naked_domain
    
    return None

def scrape_product(url):
    """
    Takes a product/listing URL and returns a dictionary:
    {
        "name": ...,
        "image": ...,
        "price": ...
    }
    Returns None if scraping fails.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Request failed:", e)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Try to extract JSON-LD data first (common for structured product info)
    json_ld = soup.find("script", type="application/ld+json")
    if json_ld:
        try:
            data = json.loads(json_ld.string)
            # Some sites have an array of objects
            if isinstance(data, list):
                data = data[0]

            name = data.get("name")
            image = data.get("image")
            price = None
            if "offers" in data and isinstance(data["offers"], dict):
                price = data["offers"].get("price")
            
            if name or image or price:
                return {"name": name, "image": image, "price": price}
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    # 2. Fallback: scrape HTML manually
    # This part may need to be customized per site
    name_tag = soup.find("h1") or soup.find("title")
    name = name_tag.text.strip() if name_tag else None

    image_tag = soup.find("img")
    image = image_tag["src"] if image_tag and image_tag.has_attr("src") else None

    store = get_store_from_url(url)
    if (store == "target"):
        # loop through all the script tags and search for price data.
        for script in soup.find_all("script"):
            # short_name = extract_target_short_name(script.string or "")
            # if (short_name != ""):
                # name = short_name
            name = shorten_name(name)
            price = extract_target_price_from_script(script.string or "")
            print(price)
            if price is not None:
                break
    elif (store == "walmart"):
        product = scrape_walmart(url)
        name = product.get('name')
        name = shorten_name(name)
        price = product.get('price')
        image = product.get('image')
    elif (store == 'amazon'):
        product = scrape_amazon(url)
        if (product):
            soup = product.get('soup') # updated soup from more specific amazon scraping function.
            price = product.get('price')
        if (price):
            price = price.replace("$", "")
        name_tag = soup.find(id="productTitle")
        if (name_tag):
            name = name_tag.text.strip()
        image_tag = soup.find(id="landingImage")
        if (image_tag):
            image_data = image_tag.get("data-a-dynamic-image")
            image = extract_amazon_image_from_dynamic_image_attr(image_data)
    else:
        price_tag = soup.find(class_="price") or soup.find("span", {"id": "price"})
        price = price_tag.text.strip() if price_tag else None

    if not any([name, image, price]):
        return None  # nothing found

    return {"name": name, "image": image, "price": price}