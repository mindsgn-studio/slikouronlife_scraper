import requests
from bs4 import BeautifulSoup

def get_page():
    response = requests.get('https://slikouronlife.co.za/artist/60224')
    content = BeautifulSoup(response.content, 'html.parser')
    print(content)

def get_details():
    pass

def get_music():
    pass

if __name__ == "__main__":
    get_page