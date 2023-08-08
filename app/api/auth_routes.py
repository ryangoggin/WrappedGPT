from flask import Blueprint, jsonify, session, request, redirect
from app.models import User, db
from app.forms import LoginForm
from app.forms import SignUpForm
from flask_login import current_user, login_user, logout_user, login_required
import random
import urllib.parse
import os
import requests
import base64

redirect_uri = "http://localhost:3000/auth/callback"
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')

auth_routes = Blueprint('auth', __name__)


def validation_errors_to_error_messages(validation_errors):
    """
    Simple function that turns the WTForms validation errors into a simple list
    """
    errorMessages = []
    for field in validation_errors:
        for error in validation_errors[field]:
            errorMessages.append(f'{field} : {error}')
    return errorMessages

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


@auth_routes.route('/')
def authenticate():
    """
    Authenticates a user.
    """
    if current_user.is_authenticated:
        return current_user.to_dict()
    return {'errors': ['Unauthorized']}


@auth_routes.route('/spotifylogin')
def login_to_spotify():
    """
    Initiate authorization request to Spotify.
    """
    state = generate_random_string(16)
    scope = 'user-read-private user-reada-email'

    # these params are explained in the spotify API docs
    params = {
        "response_type": 'code',
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state
    }

    # convert the object to the query string: "key=value,etc..."
    query_string = urllib.parse.urlencode(params)
    auth_url = 'https://accounts.spotify.com/authorize?' + query_string
    print(auth_url)

    return redirect(auth_url)


@auth_routes.route('/callback')
def spotify_callback():
    """
    Callback that implements the Access Token request (lasts for 60 minutes)
    """
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
                "redirect_uri": redirect_uri,
                "grant_type": 'authorization_code'
            },
            "headers": {
                'Authorization': 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode()).decode(),
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

        return jsonify(token_data)


@auth_routes.route('/refresh_token')
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


@auth_routes.route('/login', methods=['POST'])
def login():
    """
    Logs a user in
    """
    form = LoginForm()
    # Get the csrf_token from the request cookie and put it into the
    # form manually to validate_on_submit can be used
    form['csrf_token'].data = request.cookies['csrf_token']
    if form.validate_on_submit():
        # Add the user to the session, we are logged in!
        user = User.query.filter(User.email == form.data['email']).first()
        login_user(user)
        return user.to_dict()
    return {'errors': validation_errors_to_error_messages(form.errors)}, 401


@auth_routes.route('/logout')
def logout():
    """
    Logs a user out
    """
    logout_user()
    return {'message': 'User logged out'}


@auth_routes.route('/signup', methods=['POST'])
def sign_up():
    """
    Creates a new user and logs them in
    """
    form = SignUpForm()
    form['csrf_token'].data = request.cookies['csrf_token']
    if form.validate_on_submit():
        user = User(
            username=form.data['username'],
            email=form.data['email'],
            password=form.data['password']
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return user.to_dict()
    return {'errors': validation_errors_to_error_messages(form.errors)}, 401


@auth_routes.route('/unauthorized')
def unauthorized():
    """
    Returns unauthorized JSON when flask-login authentication fails
    """
    return {'errors': ['Unauthorized']}, 401
