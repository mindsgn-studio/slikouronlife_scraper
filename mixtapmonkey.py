
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pymongo
import re

load_dotenv()

client = pymongo.MongoClient(os.getenv('MONGO'))
db = client['mixo']


def get_page(page_number):
    response = requests.get("https://mixtapemonkey.com/artists?start="+str(page_number))
    content = BeautifulSoup(response.content, 'html.parser')
    try:
        container = content.select(".eight")
        artists = container[0].select("a")
        for artist in artists:
            artist_page = artist.attrs["href"]
            if "artists.php" in artist_page:
                pass
            else:
                go_to_artist_page(artist_page)
    except Exception as e:
        print(f"Error processing page {page_number}: {e}")
        get_page(page_number+60)
    get_page(page_number+60)


def go_to_artist_page(artist_page):
    response = requests.get("https://mixtapemonkey.com"+artist_page)
    content = BeautifulSoup(response.content, 'html.parser')
    container = content.select(".u-full-width")
    mixtapes = container[0].select("a")
    for mixtape in mixtapes:
        go_to_mixtape_page(mixtape.attrs["href"])


def go_to_mixtape_page(mixtape_page):
    response = requests.get("https://mixtapemonkey.com"+mixtape_page)
    content = BeautifulSoup(response.content, 'html.parser')
    mixtape_image = content.select_one(".mixtape-thumb")
    download = content.select_one(".download")
    album_link = download.attrs["href"]
    image = mixtape_image.select_one("img")
    cover_art = "https://mixtapemonkey.com"+image.attrs["src"]

    album_title = content.select_one("h1").text
    artist_container = content.select_one("h2")
    artist_link = artist_container.select_one("a")
    artist = artist_link.text

    save_album(artist, album_title, cover_art, album_link)
    media_player = content.select_one(".mediatec-cleanaudioplayer")
    tracks = media_player.select("li")

    for track in tracks:
        title = track.attrs["data-title"]
        track_link = "https://mixtapemonkey.com"+track.attrs["data-url"]

        match = re.match(r'^(\d+)\s*-\s*(.*)$', title)
        track_number = int(match.group(1)) if match else None
        title = match.group(2).strip() if match else None

        save_track(
            artist,
            title,
            track_number,
            track_link,
            album_title,
            cover_art
        )


def save_album(artist, album_title, cover_art, album_link):
    song_collection = db['albums']
    results = song_collection.find_one({
        "artist": artist,
        "title": album_title,
        "link": album_link,
        "coverArt": cover_art
    })

    if (results):
        pass
    else:
        response = song_collection.insert_one({
            "artist": artist,
            "title": album_title,
            "link": album_link,
            "coverArt": cover_art
        })

        if (response):
            print("saved album", artist, album_title)
            print("\n")
        else:
            pass
       

def save_track(
        artist,
        title,
        track_number,
        track_link,
        album_title,
        cover_art):
    song_collection = db['tracks']
    results = song_collection.find_one({
        "artist": artist,
        "title": title,
        "albumTitle": album_title,
        "coverArt": cover_art,
        "trackNumber": track_number,
        "link": track_link
    })

    if (results):
        pass
    else:
        response = song_collection.insert_one({
            "artist": artist,
            "title": title,
            "albumTitle": album_title,
            "coverArt": cover_art,
            "trackNumber": track_number,
            "link": track_link
        })

        if (response):
            print("saved track")
        else:
            pass
      

if __name__ == "__main__":
    page_number = 0
    get_page(page_number)
