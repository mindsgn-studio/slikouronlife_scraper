
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pymongo
from html import unescape
import random

load_dotenv()
client = pymongo.MongoClient(os.getenv('MONGO'))
db = client['mixo']


def get_page(page, number):
    response = requests.get(page)
    content = BeautifulSoup(response.content, 'html.parser')
    try:
        articles = content.select("article")
        for article in articles:
            isAudio = article.select_one(".front-view-content").text
            if ("DOWNLOAD AUDIO FILE" in isAudio or 
                "download mp3 file" in isAudio):
                link = article.select_one("a")
                go_to_page(link.attrs["href"])
    except:
        number = number + 1
        get_page("http://iminathimedia.com/?paged="+str(number), number)
    
    number = number + 1
    get_page("http://iminathimedia.com/?paged="+str(number), number)


def go_to_page(link):
    response = requests.get(link)
    content = BeautifulSoup(response.content, 'html.parser')
    try:
        download_content = content.select_one(".thecontent")
        details = content.select_one(".entry-title")
        
        decoded_string = unescape(details.text)
        artist_title = decoded_string.split(" – ")
        artist = artist_title[0]
        title = artist_title[1]
        
        link = download_content.select_one("a")
        if (".mp3" in link.attrs["href"]):
            save_track(artist, title, link.attrs["href"])
    except Exception as e:
        print(e)


def save_track(
        artist,
        title,
        track_link):
    
    song_collection = db['tracks']
    results = song_collection.find_one({
        "artist": artist,
        "title": title,
        "link": track_link
    })

    cover_art = [
        "https://images.rawpixel.com/image_800/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDIyLTA1L25zMTQ2NTEtaW1hZ2Uta3d2eWQybmIuanBn.jpg",
        "https://indieground.net/wp-content/uploads/2023/03/Freebie-GradientTextures-Preview-04.jpg",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRZpM93FCkUEcV7Cv6TPgdo4fV9N-_2tj4XhwSg0OJ_2meCu7y3aAngMhxiy3um77L_ur4&usqp=CAU",
        "https://images.unsplash.com/photo-1614850523459-c2f4c699c52e?q=80&w=1000&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxleHBsb3JlLWZlZWR8MjB8fHxlbnwwfHx8fHw%3D",
    ]

    if (results):
        pass
    else:
        response = song_collection.insert_one({
            "artist": artist,
            "title": title,
            "coverArt":  random.choice(cover_art),
            "link": track_link
        })

        if (response):
            print("saved track")
        else:
            pass


if __name__ == "__main__":
    number = 1
    get_page("http://iminathimedia.com/?paged=1", number)