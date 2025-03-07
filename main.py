import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint

load_dotenv()

### Asks user which year they would like to "travel" to
date = input('What year do you want to travel to? Type the date in this format YYYY-MM-DD:')
URL = f"https://www.billboard.com/charts/hot-100/{date}"
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}

### Scraps song titles from billboard.com hot 100 using Beautiful Soup
response = requests.get(url=URL, headers=header)
billboard_response = response.text
soup = BeautifulSoup(billboard_response, "html.parser")
song_elements = soup.find_all('h3', class_='a-truncate-ellipsis')
song_titles = [song.getText(strip=True) for song in song_elements]



### Takes list of song titles and uses Spotify API to find their URI IDs to make custom playlists
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv('SPOTIFY_ID'),
                                               client_secret=os.getenv('SPOTIFY_SECRET'),
                                               redirect_uri="http://localhost:1234",
                                               scope="user-library-read playlist-modify-public playlist-modify-private",
                                               show_dialog=True,
                                               cache_path='token.txt',
                                               username=os.getenv('USERNAME')))

user_id = sp.current_user()['id']

song_uris = []
year = date.split('-')[0]
for song in song_titles:
    result = sp.search(q=f"track:{song} year:{year}", type='track', limit=10)

    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

pprint.pp(song_uris)

### CREATE NEW PLAYLIST
playlist_name =  f'Billboard Top Tracks from {date}'
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
print(f"Playlist '{playlist_name}' created with ID: {playlist['id']}")

if song_uris:
    sp.playlist_add_items(playlist_id=playlist['id'], items=song_uris)
    print(f"{len(song_uris)} songs added to the playlist '{playlist_name}'.")

