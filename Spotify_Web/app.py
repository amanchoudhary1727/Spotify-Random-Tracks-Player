from flask import Flask, render_template, request, redirect, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

app = Flask(__name__)

CLIENT_ID = 'Your_Client_Id'
CLIENT_SECRET = 'Your_Client_Secret'
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-library-read user-modify-playback-state user-read-playback-state'

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)

sp = spotipy.Spotify(auth_manager=sp_oauth)

def get_artist_id(artist_name):
    results = sp.search(q='artist:' + artist_name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]['id']
    else:
        return None

def get_random_tracks_from_artist(artist_id, num_tracks=10):
    albums = sp.artist_albums(artist_id, album_type='album')['items']
    all_tracks = []
    
    for album in albums:
        album_tracks = sp.album_tracks(album['id'])['items']
        all_tracks.extend(album_tracks)
    
    if len(all_tracks) == 0:
        return []
    
    track_uris = [track['uri'] for track in all_tracks]
    random.shuffle(track_uris)
    
    return track_uris[:num_tracks]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    artist_names = request.form.get('artists')
    artist_names_list = artist_names.split(',')
    
    track_uris = []
    for artist_name in artist_names_list:
        artist_id = get_artist_id(artist_name.strip())
        if artist_id:
            track_uris.extend(get_random_tracks_from_artist(artist_id))
        else:
            return f"Artist {artist_name} not found", 404

    random.shuffle(track_uris)
    if len(track_uris) > 0:
        play_tracks(track_uris[:10])
        return redirect(url_for('index'))
    else:
        return "No tracks found", 404

def play_tracks(track_uris):
    devices = sp.devices()
    if len(devices['devices']) > 0:
        device_id = devices['devices'][0]['id']
    else:
        print("No devices available")
        return

    sp.start_playback(device_id=device_id, uris=track_uris)

if __name__ == '__main__':
    app.run(debug=True)
