
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
    page_url = f'https://fakaza.me/category/download-mp3/page/{page_number}'
    print(page_url, flush=True)

    try:
        response = requests.get(page_url)
        response.raise_for_status()
        content = BeautifulSoup(response.content, 'html.parser')
        container = content.select("article")

        for article in container:
            article_link = article.select_one("a").attrs['href']
            new_page = requests.get(article_link)
            new_page.raise_for_status()
            track_page = BeautifulSoup(new_page.content, 'html.parser')
            main_content = track_page.select_one(".mh-content")
            article_section = main_content.select_one('article')
            name = get_artist_name(article_section)
            title = get_title(article_section)
            cover_art = get_cover_art(main_content)
            link = get_link(main_content)
            save_music(name, title, link, cover_art, article_link)
            time.sleep(2)

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")

    page_number += 1
    get_page(page_number)

def get_artist_name(article_section):
    artist_and_title = article_section.select_one('.entry-title').text
    delimiter = " – "
    start_index = artist_and_title.rfind(delimiter)

    if start_index != -1:
        return artist_and_title[:start_index]

    return None
    
def get_title(article_section):
    artist_and_title = article_section.select_one('.entry-title').text
    delimiter = " – "
    end_index = artist_and_title.rfind(delimiter)

    if end_index != -1:
        return artist_and_title[end_index + len(delimiter):]

    return None

def get_cover_art(main_content):
    try:
        artwork_container = main_content.select_one(".entry-thumbnail")
        art = artwork_container.select_one('img')['src']
        return art
    except AttributeError:
        return None
    
def get_link(main_content):
    try:
        for link in main_content.find_all("a"):
            href = link.get("href")
            if href.endswith(".mp3"):
                return href
    except Exception:
        pass
    return None

def save_music(name, title, link, cover_art, article_link):
    song_collection = db['songs']

    if song_collection.find_one({"artist": [name], 'title': title}):
        print("Song already exists:", name, "-", title, flush=True)
        return None

    song_data = {
        'artistId': None,
        "artist": [name],
        'title': title,
        "album": None,
        "albumArtist": [name],
        "composer": None,
        "genre": None,
        "duration": 0,
        "link": link,
        "lyrics": None,
        "artwork": cover_art,
        "year": None,
        "size": None,
        "track": {
            "number": 1,
            "total": 1,
        },
        "diskNumber": {
            "number": 1,
            "total": 1,
        },
        "compilation": False,
        "bpm": None,
        "bitRate": None,
        "sampleRate": None,
        "channels": None,
        "comments": None,
        "scraped": True,
        "nft": False,
        "source": {
            "website": "https://fakaza.me", 
            "link": article_link, 
            "name": "fakaza"
        }
    }

    response = song_collection.insert_one(song_data)
    
    if response:
        print("Saved song:", name, "-", title, "ID:", response.inserted_id, flush=True)
        return response.inserted_id
    else:
        print("Failed to save song:", name, "-", title, flush=True)
        return None

if __name__ == "__main__":
    page_number = 0
    get_page(page_number)