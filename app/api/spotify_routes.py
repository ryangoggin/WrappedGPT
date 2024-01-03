from flask import Blueprint, jsonify, session, request, redirect
import random
import urllib.parse
import os
import requests
import base64
import datetime

REDIRECT_URI = "http://localhost:3000/api/spotify/callback"
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
API_BASE_URL = "https://api.spotify.com/v1/"

spotify_routes = Blueprint('spotify', __name__)


def generate_random_string(length):
    """
    generate a random string for the state in spotify login
    """
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    char_list = list(chars)
    string = ""

    for i in range(length):
        string += random.choice(char_list)

    return string


@spotify_routes.route('/login')
def login_to_spotify():
    """
    Initiate authorization request to Spotify.
    """
    state = generate_random_string(16)
    scope = 'user-read-private user-read-email'

    # these params are explained in the spotify API docs
    params = {
        "response_type": 'code',
        "client_id": CLIENT_ID,
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "show_dialog": True #for testing so can get the login over and over, remove when done testing
    }

    # convert the object to the query string: "key=value,etc..."
    query_string = urllib.parse.urlencode(params)
    auth_url = 'https://accounts.spotify.com/authorize?' + query_string
    print(auth_url)

    return redirect(auth_url)


@spotify_routes.route('/callback')
def spotify_callback():
    """
    Callback that implements the Access Token request (lasts for 60 minutes)
    """
    if "error" in request.args:
        return jsonify({"error": request.args["error"]})

    code = request.args.get('code', None)
    state = request.arg.get('state', None)

    # confirm the state matches to avoid attacks such as cross-site requst forgery (CSRF)
    if state is None:
        return redirect('/#' + urllib.parse.urlencode({"error": 'state_mismatch'}))
    else:
        auth_options = {
            "url": 'https://accounts.spotify.com/api/token',
            "data": {
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "grant_type": 'authorization_code'
            },
            "headers": {
                'Authorization': 'Basic ' + base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode(),
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "json": True
        }

        # Make a POST request to exchange the authorization code for an access token
        response = requests.post(auth_options['url'], data=auth_options['data'], headers=auth_options['headers'])
        token_data = response.json()

        # token data should have the following form:
        # {
        # "access_token": "NgCXRK...MzYjw",
        # "token_type": "Bearer",
        # "scope": "user-read-private user-read-email",
        # "expires_in": 3600,
        # "refresh_token": "NgAagA...Um_SHo"
        # }

        print(token_data)

        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_data['expires_in']

        return redirect("/profile")


@spotify_routes.route('/refresh_token')
def refresh_token():
    """
    Refreshes the token (will need to be done after 60 minutes)
    """
    refresh_token = request.args.get('refresh_token')

    auth_options = {
        "url": 'https://accounts.spotify.com/api/token',
        "headers": {
            "Authorization": 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode()).decode(),
        },
        "data": {
            "grant_type": 'refresh_token',
            "refresh_token": refresh_token
        },
        "json": True
    }

    # Make a POST request to refresh the access token
    response = requests.post(auth_options['url'], data=auth_options['data'], headers=auth_options['headers'])
    token_data = response.json()

    # token data should have the following form:
    # {
    # "access_token": "NgA6ZcYI...ixn8bUQ",
    # "token_type": "Bearer",
    # "scope": "user-read-private user-read-email",
    # "expires_in": 3600
    # }

    if response.status_code == 200:
        access_token = token_data.get('access_token')
        return jsonify({
            "access_token": access_token
        })
    else:
        return jsonify({
            "error": 'refresh token failed',
            "status_code": response.status_code
        })


@spotify_routes.route('/profile')
def get_profile():
    """
    Get the Spotify user's profile info to display.
    """
    # if no access token in session, login again
    if "access_token" not in session:
        return redirect("/login")

    # check if access token has expired
    if datetime.now().timestamp() > session['expires_at']:
        return redirect("/refresh_token")

    headers = {
        "Authorization": f"Bearer: {session['access_token']}"
    }

    response = requests.get(API_BASE_URL + 'me')
