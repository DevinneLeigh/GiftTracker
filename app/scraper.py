import re
import html
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class Scraper:
    def __init__(self, url):


        self.common_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.amazon.com/",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
        }
        self.mobile_headers = {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 "
                "Mobile/15E148 Safari/604.1"
            ),
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
    Debugging utility to write the current HTML to a file.
    Good for figuring out if you are being sent to bot detection pages.
    """
    def write_html_to_file(self):
        html_output = self.soup.prettify()
        with open("page_dump.html", "w", encoding="utf-8") as f:
            f.write(html_output)
        print("HTML written to page_dump.html")
    
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
                if name or image or price:
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
        
		# Should get name if not detected as a bot
        
        price_hidden_input = self.soup.find("input", id="twister-plus-price-data-price")
        if price_hidden_input:
            # get the value from the input element
            self.set_product(price=price_hidden_input.get("value"))
        else:
            # Fallback to mobile amazon page.
            self.scrape_amazon_mobile()

        image_tag = self.soup.find(id="landingImage")
        if (image_tag):
            image_data = image_tag.get("data-a-dynamic-image")
            image = self.extract_amazon_image_from_dynamic_image_attr(image_data)
            if image:
                self.set_product(image=image)


    def scrape_amazon_mobile(self):
        print("Falling back to mobile page scrape.")
        mobile_url = self.url.replace("www.amazon.", "m.amazon.")
        try:
            response = requests.get(mobile_url, headers=self.mobile_headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print("Request failed:", e)
            return None

        mobile_soup = BeautifulSoup(response.text, "html.parser")

        price_tag = mobile_soup.find("span", class_="aok-offscreen")
        if price_tag:
            price = price_tag.text.strip().replace("$", "")
            if price:
                self.set_product(price=price)
            

        
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

        # Customized methods for complex popular sites.
        store = self.get_store()
        if (store == "target"):
            self.scrape_target()
        elif (store == "walmart"):
            self.scrape_walmart()
        elif (store == 'amazon'):
            self.scrape_amazon()

        if not any(self.product.values()):
            return None  # nothing found
        
        # print(self.product)

        return self.product