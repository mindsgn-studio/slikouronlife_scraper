
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
    name = ""
    profile=""
    social = []
    contact = []

    response = requests.get('https://slikouronlife.co.za/artist/'+str(page_number))
    content = BeautifulSoup(response.content, 'html.parser')
    container = content.select(".container")
    if(container[3]):
        if(container[3].select(".profile-info")):
            profile_info = container[3].select(".profile-info")
        try:
            if(profile_info[0].select("h2")):
                name = profile_info[0].select("h2")[0].text
        except UnboundLocalError:
            page_number = page_number+1
            print('failed page', page_number)
            time.sleep(5)
            get_page(page_number)
            

        if(profile_info[0].select_one("img")):
            profile = profile_info[0].select_one("img").attrs['src']
        
        if(profile_info[0].select_one('.social-container')):
            socials = profile_info[0].select_one('.social-container')
            
            if(socials.select("a")):
                for item in socials.select("a"):
                    social.append(item.attrs['href'])
        
        if(profile_info[0].select_one('.profile-contact')):
            contact_details = profile_info[0].select('.profile-contact')
            if(contact_details[0].select('b')):
               for item in contact_details[0].select('b'):
                    contact.append(item.text)
        
        id = save_details(name, profile, social, contact)
       
        if(container[3].select('.player-controls')):
            list = container[3].select('.player-controls')
            for item in list:
                if(item.select_one('a')):
                    if(item.select_one('a').attrs['data-type'] == "track"):
                        results = save_music(id, item.select_one('a').attrs['data-artist'], item.select_one('a').attrs['data-title'], item.select_one('a').attrs['data-source'],  item.select_one('a').attrs['data-song-image'])

    page_number = page_number+1
    print('sleeping')
    time.sleep(5)
    get_page(page_number)

def save_details(name, profile, social, contact):
    artist_collection = db['artists']
    results = artist_collection.find_one({'name': name, "contact": contact})
    if(results):
        return results['_id']
    else:
        response = artist_collection.insert_one({"name": name, "profile": profile, "social": social, "contact": contact})
        if(response):
            print("saved artist", response.inserted_id)
            return response.inserted_id
        else:
            return False

def save_music(id ,name, title, link, cover_art):
    song_collection = db['tracks']
    results = song_collection.find_one({'artistId': id, "name": name, 'title': title, "link": link,  "art": cover_art})
    if(results):
        pass
    else:
        response = song_collection.insert_one({'artistId': id, "name": name, 'title': title, "link": link,  "art": cover_art, "source": { "link": "slikouronlife.co.za", "name": "slikouronlife.co.za" } })
        if(response):
            print("saved track", response.inserted_id)
            return response.inserted_id
        else:
            return False

if __name__ == "__main__":
    page_number = 0
    page_number=int(sys.argv[1])
    get_page(page_number)