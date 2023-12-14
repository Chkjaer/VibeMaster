import pprint

from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template, request, redirect, session, url_for
import urllib.parse, urllib.request, urllib.error, json
from projectsecrets import spotify_client_id, spotify_client_secret, secret_key, unsplash_access_key

app = Flask(__name__)
app.secret_key = secret_key

oauth = OAuth(app)
oauth.register(
    name="spotify",
    client_id=spotify_client_id,
    client_secret=spotify_client_secret,
    authorize_url="https://accounts.spotify.com/authorize",
    access_token_url="https://accounts.spotify.com/api/token",
    api_base_url="http://api.spotify.com/v1/",
    client_kwargs={
        'scope': 'streaming user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control'
    }
)

@app.route("/login")
def login():
    redirect_uri = url_for('authorize', _external=True)
    print(redirect_uri)
    return oauth.spotify.authorize_redirect(redirect_uri)

@app.route("/spotify-authorize")
def authorize():
    token = oauth.spotify.authorize_access_token()
    session["spotify-token"] = token
    return redirect(url_for('index'))

@app.route("/")
def index():
    try:
        token = session["spotify-token"]
    except KeyError:
        return redirect(url_for("login"))
    return render_template('home.html')

@app.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "POST":
        query = request.form['query']
        image_data = get_image_data(query)
        write_background_image_css('static/background.css', image_data['image_url'])
        playlist_data = get_playlist_data(query)
        device_id = get_device_id()
        start_playback(playlist_data[1], device_id)
        return render_template("result.html", query=query.capitalize(), access_token=session["spotify-token"],
                               playlist_url=playlist_data[2], image=playlist_data[0], device_id=device_id,
                               photo_by=image_data['photo_by'], credit_link=image_data['credit_link'])
    elif request.method == "GET":
        return "Wrong HTTP method"

def get_playlist_data(query):
    base_url = 'https://api.spotify.com'
    params = {'q': query + ' vibes', 'type': "playlist", 'limit': 1}
    paramstr = urllib.parse.urlencode(params)
    request_url= 'search?' + paramstr
    result_data = json.loads(oauth.spotify.get(request_url, token=session['spotify-token']).text)
    playlist_data = result_data['playlists']['items'][0]
    pprint.pprint(playlist_data)
    playlist_uri = playlist_data['uri']
    playlist_url = playlist_data['external_urls']['spotify']
    image_url = playlist_data['images'][0]['url']
    return (image_url, playlist_uri, playlist_url)

def get_device_id():
    devices_data = oauth.spotify.get('me/player/devices', token=session['spotify-token']).text
    return json.loads(devices_data)['devices'][0]['id']

def start_playback(playlist_uri, device_id):
    json_data = {'context_uri': playlist_uri}
    headers = {'Authorization': 'Bearer ' + str(session['spotify-token'])}
    url = f'https://api.spotify.com/v1/me/player/play?'
    response = oauth.spotify.put(url, json=json_data, token=session['spotify-token'], headers=headers)
    # Check the response status
    if response.status_code == 204:
        print('Playback started successfully!')
    else:
        print(f'Error starting playback: {response.status_code}, {response.json()}')

def get_image_data(query):
    base_url = 'https://api.unsplash.com/photos/random'
    params = {'client_id': unsplash_access_key, 'query': query, 'orientation': 'landscape', 'count': 1, }
    paramstr = urllib.parse.urlencode(params)
    request_url= base_url + "/?" + paramstr
    print(request_url)
    response = urllib.request.urlopen(request_url).read().decode('utf-8')
    image_data = json.loads(response)[0]
    pprint.pprint(image_data)
    image_info = {'image_url': image_data['urls']['full'],
                  'photo_by': image_data['user']['name'],
                  'credit_link': image_data['user']['links']['html']}
    print(image_info)
    return image_info

def write_background_image_css(file_path, image_url):
    css_content = f"""
.background {{
    background-image: url('{image_url}');
    background-size: cover;
}}
"""
    # Write CSS content to the file
    with open(file_path, 'w') as css_file:
        css_file.write(css_content)