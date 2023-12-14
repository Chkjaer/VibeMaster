from authlib.integrations.requests_client import OAuth2Session

from OAuthtest1 import client_id, client_secret # Keep these in a separate file
# https://developer.spotify.com/documentation/general/guides/authorization/scope
scope = "playlist-read-private"

client = OAuth2Session(client_id, client_secret, scope=scope, redirect_uri="https://chkjaer.pythonanywhere.com/spotify")
authorization_endpoint = "https://accounts.spotify.com/authorize"
uri, state = client.create_authorization_url(authorization_endpoint)
print("Please go to this URL in your web broswer and follow the prompts:{}".format(uri))

authorization_response = input("Once you are redirected by your browser, copy the URL from you browser's address bar and enter it here:")

token_endpoint = "https://accounts.spotify.com/api/token"
token = client.fetch_token