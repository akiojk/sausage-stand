from types import SimpleNamespace
import requests
import sys
import json
import math
import re
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


PAGE_SIZE = 50
CLIENT_ID = ""


class StockLevel:
    def __init__(self, stock_level, store_name, store_address, store_phone):
        self.stock_level = 0 if not stock_level or math.isnan(
            stock_level) else stock_level
        self.store_name = store_name
        self.store_address = store_address
        self.store_phone = store_phone

    def to_string(self):
        return f"{f'✅ In Stock ({self.stock_level})' if self.stock_level > 0 else '🚫 OOS'} 👉 {self.store_name} (📍 {self.store_address}) 📱{self.store_phone}"


def get_guest_token(url):
    chrome_options = Options()
    chrome_options.headless = True
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    token_json = WebDriverWait(driver, timeout=120).until(
        lambda d: d.get_cookie('guest-token-storage'))['value']
    return json.loads(token_json, object_hook=lambda d: SimpleNamespace(**d)).token


def get_stock_url(host, current_page=1):
    sanitised_host = host.replace("www.", "")
    return f"https://api.prod.{sanitised_host}/v1/stores/products/stock?latitude=-36&longitude=135&currentPage={current_page}&fields=FULL&pageSize={PAGE_SIZE}&isTrCart=false&tradeRestrictedStore=&isPickup=true&radius=3000000"


def extract_stock_level_list(page_json):
    stock_level_list = []
    for store in page_json.data.stores:
        stock_level = StockLevel(
            store.products[0].stock.stockLevel, store.displayName, store.address.formattedAddress, store.address.phone)
        stock_level_list.append(stock_level)
    return stock_level_list


def load_page_json(host, page_number=1):
    first_page_request = requests.post(get_stock_url(host, page_number), headers=headers,
                                       data=f'{{"products":["{product_code}"]}}')
    return json.loads(
        first_page_request.text, object_hook=lambda d: SimpleNamespace(**d))


entire_stock_level_list = []
in_stock_only = False

if not CLIENT_ID:
    print("Please obtain clientId from the sausage website and insert at line 16 of this script")
    sys.exit(1)

if len(sys.argv) == 1:
    print(f"Run: python3 {sys.argv[0]} <url> [instock only: yes]")
    sys.exit(1)

if len(sys.argv) == 3:
    in_stock_only = True if sys.argv[2] == "yes" else False

url = urlparse(sys.argv[1])
product_code = re.sub('.+_p(\d+)$', '\\1', url.path)

auth_token = get_guest_token(f"{url.scheme}://{url.netloc}")

headers = {
    'Authorization': f'Bearer {auth_token}',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    'clientId': CLIENT_ID,
    'country': 'AU',
    'currency': 'AUD',
    'locale': 'en_AU',
    'stream': 'RETAIL',
    'userId': 'anonymous'
}

first_page_json = load_page_json(url.hostname)
entire_stock_level_list = extract_stock_level_list(first_page_json)

total_pages = first_page_json.data.pagination.totalPages
current_page = 2

while current_page < total_pages:
    current_page_json = load_page_json(url.hostname, current_page)
    entire_stock_level_list += extract_stock_level_list(current_page_json)
    current_page += 1


for index, stock_level_info in enumerate(entire_stock_level_list if not in_stock_only else [item for item in entire_stock_level_list if item.stock_level > 0]):
    print(f"{index + 1}. {stock_level_info.to_string()}")
