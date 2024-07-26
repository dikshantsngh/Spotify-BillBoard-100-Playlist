import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from random import randint
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv('.env')

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


year = input(
    'Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ')


def scapping_billboard_100(year):
    url = "https://www.billboard.com/charts/hot-100/"

    response = requests.get(f"{url}{year}")
    billboard_web_page = response.text

    soup = BeautifulSoup(billboard_web_page, 'html.parser')

    song_list = soup.select(
        selector='li ul li h3')

    artist_list = soup.select(
        selector='li span.a-no-trucate')

    song_titles = [song.get_text().strip()
                   for song in song_list]
    artist_names = [artist.get_text().strip()
                    for artist in artist_list]

    return zip(song_titles, artist_names)


def main():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope='playlist-modify-private',
            redirect_uri='https://example.com/',
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            show_dialog=True,
            cache_path='token.txt'
        )
    )
    user_id = sp.current_user()['id']  # type: ignore

    songs_uri = []
    billboard_100 = scapping_billboard_100(year)
    for song, artist in billboard_100:
        result = sp.search(
            q=f"track%3F{song}%2520artist%3F{artist}", type="track", limit=1)
        try:
            uri = result['tracks']['items'][0]['id']  # type: ignore
            songs_uri.append(uri)
        except IndexError:
            print(f"{song} by {artist} doesn't exist in Spotify. Skipped\n")

    playlist = sp.user_playlist_create(
        user=user_id, name=f"BillBoard 100 {year.split('-')[0]}", public=False)

    sp.playlist_add_items(
        playlist_id=playlist['id'], items=songs_uri)  # type: ignore


if __name__ == "__main__":
    main()
