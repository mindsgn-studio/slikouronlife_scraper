
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pymongo
import time
import sys

load_dotenv()

client = pymongo.MongoClient(os.getenv('MONGO'))
db = client['mixo']


def get_page(page_number):
    response = requests.get('https://slikouronlife.co.za/artist/'+str(page_number))
    content = BeautifulSoup(response.content, 'html.parser')
    try:
        container = content.select(".card--song")
        for item in container:
            # Process each item here
            data = item.select_one(".card__play")           
            title = data.attrs['data-title']
            artist = data.attrs['data-artist']
            artist_id = data.attrs['data-artist-id']
            art = data.attrs['data-song-image']
            song_id = data.attrs['data-song-id']
            save_music(artist_id, artist, title, art, song_id)
    except Exception as e:
        print(f"Error processing page {page_number}: {e}")
        get_page(page_number+1)
    get_page(page_number+1)


def save_music(artist_id, artist, title, cover_art, song_id):
    song_collection = db['tracks']
    results = song_collection.find_one({
        "id": artist_id,
        "artist": artist,
        "title": title,
        "download": "https://slikouronlife.co.za/play-song/"+song_id,
        "play": "https://slikouronlife.co.za/download-song/"+song_id,
        "art": cover_art
    })

    if (results):
        pass
    else:
        print(artist, title)
        response = song_collection.insert_one({
            "id": artist_id,
            "artist": artist,
            "title": title,
            "download": "https://slikouronlife.co.za/play-song/"+song_id,
            "play": "https://slikouronlife.co.za/download-song/"+song_id,
            "art": cover_art,
            "source": {
                "link": "slikouronlife.co.za",
                "name": "slikouronlife.co.za"
            }
        })

        if (response):
            print("saved track", response.inserted_id)
            return response.inserted_id
        else:
            return False

if __name__ == "__main__":
    page_number = 0
    get_page(page_number)
