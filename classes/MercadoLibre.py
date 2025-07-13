import requests
from bs4 import BeautifulSoup

class MercadoLibre():
    url = 'https://www.mercadolibre.com.uy/'

    def get_product_details(self, product_url):
        # user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(product_url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch product details: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', class_='ui-pdp-title').get_text(strip=True)
        price = soup.find('meta', itemprop='price').get('content')
        img = soup.find('img', class_='ui-pdp-image').get('src')
        
        return {
            'title': title,
            'current_price': float(price),
            'url': product_url,
            'img': img,
        }