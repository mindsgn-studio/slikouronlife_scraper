import requests
from bs4 import BeautifulSoup

def get_page(page_number):
    name = ""
    profile={}
    social = []
    contact = []

    response = requests.get('https://slikouronlife.co.za/artist/'+str(page_number))
    content = BeautifulSoup(response.content, 'html.parser')
    container = content.select(".container")
    if(container[3]):
        if(container[3].select(".profile-info")):
            profile_info = container[3].select(".profile-info")
        if(profile_info[0].select("h2")):
            name = profile_info[0].select("h2")[0].text
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
        
        if(container[3].select('.player-controls')):
            list = container[3].select('.player-controls')
            for item in list:
                if(item.select_one('a')):
                    if(item.select_one('a').attrs['data-type'] == "track"):
                        pass
                    if(item.select_one('a').attrs['data-type'] == "videoModal"):   
                        pass
    
    print(name, profile, social, contact, page_number)
    page_number = page_number+1
    get_page(page_number)

def save_details(name, profile):
    pass

def save_music(id ,name, music):
    pass

def save_video(id, name, music):
    pass

if __name__ == "__main__":
    page_number = 60224
    get_page(page_number)