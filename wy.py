import requests
from bs4 import BeautifulSoup
url = "http://books.toscrape.com/"
response = requests.get(url)
response.coding = "utf-8"
soup = BeautifulSoup(response.text,'html.parser')
books = soup.find_all('article',class_='product_pod')
for book in books:
    title = book.h3.a['title']
    price = book.find('p',class_='price_color').text
    print(f"书名：{title}")
    print(f"价格：{price}")
    print("-"*30)
