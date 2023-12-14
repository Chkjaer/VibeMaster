import urllib.parse, urllib.request, urllib.error, json

def get_spotify_data(query):
    base_url = 'https://api.spotify.com'
    params = {'q': query, type: "playlist", 'limit': 1}
    paramstr = urllib.parse.urlencode(params)
    request_url = base_url + '/search?' + paramstr
    response_string = urllib.request.urlopen(request_url).read().decode('utf-8')
    result_data = json.loads(response_string)
    print(result_data)
    return result_data

def safe_get_spotify_data(query):
    try:
        safe_data = get_spotify_data(query)
        return safe_data
    except urllib.error.HTTPError as e:
        print('Error trying to retrieve data: ' + str(e))
        return
    except urllib.error.URLError as e:
        print('Error trying to retrieve data: ' + str(e))
        return