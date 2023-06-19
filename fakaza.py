
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pymongo
import time
import sys

load_dotenv()

client = pymongo.MongoClient(os.getenv('MONGO'))
db = client['mixo-dev']

def get_page(page_number):
    response = requests.get('https://fakaza.me/category/download-mp3/page/'+str(page_number))
    content = BeautifulSoup(response.content, 'html.parser')
    container = content.select("article")
    
    for article in container:
        article_link = article.select_one("a")
        new_page = requests.get(article_link.attrs['href'])
        track_page = BeautifulSoup(new_page.content, 'html.parser')
        main_content = track_page.select(".mh-content")
        print(main_content)
        time.sleep(2)

    page_number=page_number+1
    get_page(page_number)

if __name__ == "__main__":
    page_number = 0
    page_number=int(sys.argv[1])
    get_page(page_number)