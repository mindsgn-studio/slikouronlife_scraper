import os
from gql import gql, Client
from dotenv import load_dotenv
from gql.transport.aiohttp import AIOHTTPTransport
import pymongo
import time
import asyncio
from asyncio import Queue

load_dotenv()

after_cursor = None

client = pymongo.MongoClient(os.getenv('MONGO'))
db = client[os.getenv('ENVIRONMENT')]

async def process_token(token, collection_address):
    metadata = token.get('metadata', {})
    if metadata:
        try:
            title = metadata['name']
            artist = metadata['artist_name']
            art = metadata['image']
            link = metadata['audio_url']
            print(token)
            # await save_music(artist, title, link, art, collection_address)
        except KeyError as e:
            print(f"Error accessing metadata: {e}")

async def graphQLQuery(queue):
    global after_cursor
    transport = AIOHTTPTransport(url="https://api.zora.co/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql(
        """
        query MyQuery($afterCursor: String) {
        tokens(pagination: {limit: 5, after: $afterCursor}, filter: {mediaType: AUDIO}) {
            nodes {
            token {
                collectionAddress
                tokenId
                name
                owner
                image {
                url
                }
                metadata
                tokenStandard
                tokenUrl
                tokenUrlMimeType
                networkInfo {
                chain
                network
                }
            }
            }
            pageInfo {
            endCursor
            hasNextPage
            limit
            }
        }
        }
    """)

    try:
        result = await client.execute_async(query, variable_values={'afterCursor': after_cursor})
        tokens = result.get('tokens', {}).get('nodes', [])

        for token in tokens:
            token_data = token.get('token', {})
            collection_address = token_data.get('collectionAddress')
            await process_token(token_data, collection_address)

        after_cursor = result.get('tokens', {}).get('pageInfo', {}).get('endCursor')
        

        await queue.put(None)

    except Exception as e:
        print(f"GraphQL query error: {e}")
        await graphQLQuery(queue)

async def save_music(name, title, link, cover_art, collection_address, nft ):
    song_collection = db['songs']
    results = song_collection.find_one({"artist": [name], 'title': title})
    if(results):
        pass
    else:
        response = song_collection.insert_one(
            {
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
                "nft": nft,
                "source": {
                    "website": "https://market.zora.co/", 
                    "link": "https://market.zora.co/"+collection_address, 
                    "name": "zora"
                } })
        if(response):
            print("saved song", response.inserted_id)

async def main():
    queue = Queue(maxsize=120)
    await queue.put(None) 

    while True:
        await queue.get() 
        await graphQLQuery(queue)

if __name__ == "__main__":
   asyncio.run(main())