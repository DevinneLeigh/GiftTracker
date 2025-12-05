import re
import html
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class Scraper:
    def __init__(self, url):


        self.common_headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
        }

        self.url = url
        self.soup = None

        self.product = {
            "name": None,
            "image": None,
            "price": None
        }
    
    def set_product(self, name=None, image=None, price=None):
        if name is not None:
            self.product['name'] = name
        if image is not None:
            self.product['image'] = image
        if price is not None:
            self.product['price'] = price
    
    @classmethod
    def shorten_name(cls, text: str) -> str | None:
        return text.split(",")[0]
    
    """
        Extracts the naked TLD of a URL, e.g., 'amazon', 'walmart', 'target'.
        Returns None if the domain is not recognized.
    """
    def get_store(self) -> str | None:
        domain = urlparse(self.url).netloc.lower()
        
        # Remove 'www.' prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
        
        # Take only the part before the first '.'
        naked_domain = domain.split(".")[0]
        
        # Only return if it's one of the known stores
        if naked_domain in ["amazon", "walmart", "target"]:
            return naked_domain
        
        return None
    

    """
        Try to extract JSON-LD data first (common for structured product info)
    """
    def get_structured_data_product(self):
        json_ld = self.soup.find("script", type="application/ld+json")
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                # Some sites have an array of objects
                if isinstance(data, list):
                    data = data[0]

                name = self.shorten_name(data.get("name"))
                image = data.get("image")
                price = None
                if "offers" in data and isinstance(data["offers"], dict):
                    price = data["offers"].get("price")

                if name and image and price:
                    print("🫠🫠🫠🫠🫠🫠 WOWIE THIS WORKS?!")
                
                if name or image or price:
                    print("😵‍💫 Well, almost. 😵‍💫")
                    self.set_product(name=name, image=image, price=price)
                    return {"name": name, "image": image, "price": price}
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
    

    def generalized_scrape_attempt(self):
        if (self.product['name'] == None):
            name_tag = self.soup.find("h1") or self.soup.find("title")
            if name_tag:
                self.set_product(name=self.shorten_name(name_tag.text.strip()))
        if (self.product['image'] == None):
            og_image = self.soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                self.set_product(image=og_image["content"])
    

    """
        Extracts the current_retail price from a Target script tag string.
        Returns a float price, or None if not found.
    """
    def extract_target_price_from_script(self, script_text: str) -> float | None:
        match = re.search(r'\\"price\\":\{\\"current_retail\\":([\d\.]+)', script_text)
        if match:
            return float(match.group(1))
        return None
    
    def scrape_target(self):

        # Name should be good.
        # Image should be good.

        # loop through all the script tags and search for price data.
        for script in self.soup.find_all("script"):
            p=self.extract_target_price_from_script(script.string or "")
            print(p)
            self.set_product(price=p)
            if self.product['price'] is not None:
                break # stop looping scripts if we found price.
    
    
    
    def scrape_walmart(self):

        script = self.soup.find("script", id="__NEXT_DATA__")

        if not script:
            return None  # Bot blocked or unusual page

        data = json.loads(script.string)

        try:
            product = data["props"]["pageProps"]["initialData"]["data"]["product"]
            self.set_product(name=product.get("name"), price=product.get("priceInfo", {}).get("currentPrice", {}).get("price"), image=product.get("imageInfo", {}).get("thumbnailUrl"))

            return {
                "name": product.get("name"),
                "price": product.get("priceInfo", {}).get("currentPrice", {}).get("price"),
                "image": product.get("imageInfo", {}).get("thumbnailUrl"),
            }
        except Exception as e:
            print("Parsing error:", e)
            return None
        
    
    """
        Extracts the first image URL from Amazon's 'data-a-dynamic-image' attribute
        when it is HTML-encoded.
    """
    def extract_amazon_image_from_dynamic_image_attr(self, attr_value: str) -> str | None:
        if not attr_value:
            return None

        decoded = html.unescape(attr_value)

        # Capture full quoted URL
        match = re.search(r'"(https://m\.media-amazon\.com[^"]+)"', decoded)
        if match:
            return match.group(1)

        return None
    


    def scrape_amazon(self):
        price = None 

        price_container = self.soup.find("span", id="tp_price_block_total_price_ww")
        if price_container:
            price_tag = price_container.find("span", class_="a-offscreen")
            if price_tag:
                price = price_tag.get_text(strip=True)

        try:
            return {
                "price": price,
            }
        except Exception as e:
            print("Parsing error:", e)
            return None
        
    """
        Takes a product/listing URL and returns a dictionary:
        {
            "name": ...,
            "image": ...,
            "price": ...
        }
        Returns None if scraping fails.
    """
    def scrape_product(self):
        
        # Get the page and save the response as soup.
        try:
            response = requests.get(self.url, headers=self.common_headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print("Request failed:", e)
            return None

        self.soup = BeautifulSoup(response.text, "html.parser")

        # 1. Try to extract JSON-LD data first (common for structured product info)
        self.get_structured_data_product()

        # 2. Fallback: scrape HTML manually
        self.generalized_scrape_attempt()

        print("Before getting specific, we found: ")
        print(self.product)

        # Customized methods for complex popular sites.
        store = self.get_store()
        if (store == "target"):
            self.scrape_target()
        elif (store == "walmart"):
            product = self.scrape_walmart()
            name = product.get('name')
            name = self.shorten_name(name)
            price = product.get('price')
            image = product.get('image')
        elif (store == 'amazon'):
            product = self.scrape_amazon()
            if (product):
                price = product.get('price')
            if (price):
                price = price.replace("$", "")
            name_tag = self.soup.find(id="productTitle")
            if (name_tag):
                name = name_tag.text.strip()
            image_tag = self.soup.find(id="landingImage")
            if (image_tag):
                image_data = image_tag.get("data-a-dynamic-image")
                image = self.extract_amazon_image_from_dynamic_image_attr(image_data)
        else:
            price_tag = self.soup.find(class_="price") or self.soup.find("span", {"id": "price"})
            price = price_tag.text.strip() if price_tag else None

        if not any(self.product.values()):
            return None  # nothing found
        
        print("After getting specific, we found: ")
        print(self.product)

        return self.product