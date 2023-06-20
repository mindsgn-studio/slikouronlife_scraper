
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pymongo
import time
import sys

load_dotenv()

client = pymongo.MongoClient(os.getenv('MONGO'))
db = client[os.getenv('ENVIRONMENT')]

def get_page(page_number):
    print('https://fakaza.me/category/download-mp3/page/'+str(page_number))
    response = requests.get('https://fakaza.me/category/download-mp3/page/'+str(page_number))
    content = BeautifulSoup(response.content, 'html.parser')
    container = content.select("article")
    
    for article in container:
        article_link = article.select_one("a").attrs['href']
        new_page = requests.get(article_link)
        track_page = BeautifulSoup(new_page.content, 'html.parser')
        main_content = track_page.select_one(".mh-content")
        article_section = main_content.select_one('article')
        name = get_artist_name(article_section)
        title = get_title(article_section)
        cover_art = get_cover_art(main_content)
        link = get_link(main_content)
        save_music(name, title, link, cover_art, article_link)
        time.sleep(2)

    page_number=page_number+1
    get_page(page_number)

def get_artist_name(article_section):
    artist_and_title = article_section.select_one('.entry-title').text
    delimiter = " – "
    start_index = artist_and_title.rfind(delimiter)

    if start_index != -1:
        extracted_substring = artist_and_title[:start_index]
        return extracted_substring
    return None
    
def get_title(article_section):
    artist_and_title = article_section.select_one('.entry-title').text
    delimiter = " – "
    end_index = artist_and_title.rfind(delimiter)

    if end_index != -1:
        extracted_substring = artist_and_title[end_index + len(delimiter):]
        return extracted_substring
    return None

def get_cover_art(main_content):
    try:
        artwork_container = main_content.select_one(".entry-thumbnail")
        art = artwork_container.select_one('img').attrs['src']
        return art
    except:
        return None
    
def get_link(main_content):
    try:
        for link in main_content.find_all("a"):
            href = link.get("href")
            if href.endswith(".mp3"):
                return (href)
    except:
        return None

def test_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status() 
        print("Download successful!")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    pass

def save_music(name, title, link, cover_art, article_link):
    song_collection = db['tracks']
    results = song_collection.find_one({"name": name, 'title': title})
    if(results):
        pass
    else:
        response = song_collection.insert_one({'artistId': None, "name": name, 'title': title, "link": link,  "art": cover_art, "source": { "website": "https://fakaza.me", "link": article_link, "name": "fakaza" } })
        if(response):
            print("saved track", response.inserted_id)
            return response.inserted_id
        else:
            return False

if __name__ == "__main__":
    page_number = 0
    get_page(page_number)
    
