from pprint import pprint
from functools import wraps
import dateutil.parser
import json
import os
import validators
import urllib

from flask import Flask, send_from_directory, jsonify, request, session, redirect, url_for
import redis
import requests


REDIS_ITEM_EXPIRE_TIME = 3600 * 24 * 7  # seconds
CLOJURE_APP = 'http://localhost:3000'

# Documentation: https://developers.google.com/identity/protocols/OAuth2WebServer
# GOOGLE_OAUTH2_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
# GOOGLE_TOKEN_ENDPOINT = 'https://www.googleapis.com/oauth2/v4/token'
# todo: absolute path
GOOGLE_CLIENT_INFO = json.load(open('config/client_secret.json', 'r'))
GOOGLE_USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'


app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get('APP_SECRET_KEY') or os.urandom(24)


def get_redis():
    return redis.StrictRedis(host='localhost', port=6379, db=0)


def get_new_items_redis():
    redis_db = get_redis()
    new_item_keys = redis_db.keys('new:item:*')
    res = [redis_db.hgetall(key) for key in new_item_keys]
    return res


def archive_item_redis(item_id):
    redis_db = get_redis()
    new_item_key = 'new:item:{}'.format(item_id)
    old_item_key = 'old:item:{}'.format(item_id)
    return redis_db.renamenx(new_item_key, old_item_key)


def update_database(data):
    redis_db = get_redis()
    for _id, item in data.iteritems():
        # pprint(item)
        key_old_item = 'old:item:{}'.format(_id)
        key_new_item = 'new:item:{}'.format(_id)
        if item['price'] != redis_db.hget(key_old_item, 'price'):
            redis_db.delete(key_old_item)
            redis_db.hmset(key_new_item, item)
            redis_db.expire(key_new_item, REDIS_ITEM_EXPIRE_TIME)
            # gcm_notify(DEVICE_TOKEN, item['title'])


def oauth_required(fn):
    """A wrapper for all route handler that expect user's info in the session"""
    @wraps(fn)
    def decorator(*args, **kwargs):
        if 'user' not in session:
            print 'redirect for user'  # todo remove print
            return redirect(url_for('oauth2callback'))
        return fn(*args, **kwargs)
    return decorator


def extract_json_data(response):
    """
    :params response: requests.response
    """
    if response.status_code != 200:
        raise ValueError(response.text)
    return json.loads(response.text)


def get_google_auth_uri():
    """
    Get the URL for Google authentication
    
    :rtype: basestring
    """
    info = GOOGLE_CLIENT_INFO['web']
    params = {
        'scope': 'profile',
        'redirect_uri':  'http://localhost:5000/oauth2callback',
        'response_type': 'code',
        'client_id': info['client_id']
    }
    return info['auth_uri'] + '?' + urllib.urlencode(params)


def get_token_access(auth_code):
    """Exchange OAuth authentication code for access token"""
    info = GOOGLE_CLIENT_INFO['web']
    data = {
        'code': auth_code,
        'client_id': info['client_id'],
        'client_secret': info['client_secret'],
        'redirect_uri': 'http://localhost:5000/oauth2callback',
        'grant_type': 'authorization_code'
    }
    resp = requests.post(info['token_uri'], data=data)
    return extract_json_data(resp)


def get_google_user_info(access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }
    resp = requests.get(GOOGLE_USER_INFO, headers=headers)
    return extract_json_data(resp)


@app.route('/')
def index():
    print session
    return jsonify(session.get('user', {}))
    return app.send_static_file('index.html')

# @app.route('/test')
# def delay():
#     page = int(request.args.get('page', 1))
#     print '----------', page
#     time.sleep(1)
#     res = [] if page == 10 else [page]
#     return json.dumps(res)


@app.route('/<path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/api/me', methods=['GET'])
@oauth_required
def get_user_session_info():
    print session
    print session.get('user')
    return jsonify(session.get('user', {}))


@app.route('/api/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    print session  # todo remove code
    return jsonify({})


@app.route('/api/new-item/', methods=['GET'])
# @oauth_required
def get_new_items():
    new_items = sorted(get_new_items_redis(),
                       key=lambda x: dateutil.parser.parse(x['time']),
                       reverse=True)
    return jsonify({'items': new_items})


@oauth_required
@app.route('/api/scrape-link', methods=['POST'])
def retrieve_items():
    query_link = request.get_json().get('link')
    if not validators.url(query_link):
        return jsonify({"error": "Not valid link"}), 400
    resp = requests.post(CLOJURE_APP + '/scrape', headers={"content-type": "application/json"},
                         json={"link": query_link})
    data = json.loads(resp.text)
    update_database(data)
    return jsonify({}), 204


@oauth_required
@app.route('/api/item/<item_id>/archive', methods=['POST'])
def archive(item_id):
    success = archive_item_redis(item_id)
    if success:
        print 'archive {}'.format(item_id)
        return jsonify({}), 204
    else:
        print 'fail'
        return jsonify({'error': 'cannot archive {}'.format(item_id)}), 500


@app.route('/oauth2callback', methods=['GET'])
def oauth2callback():
    """The OAuth handler for Google OAuth2"""
    if 'code' not in request.args:
        auth_uri = get_google_auth_uri()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        credential = get_token_access(auth_code)
        user_info = get_google_user_info(access_token=credential['access_token'])
        user_attributes_filter = ['id', 'name', 'link']
        session['user'] = {k: v for k, v in user_info.items() if k in user_attributes_filter}
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=(os.environ.get('DEBUG') == 'True'), host ='0.0.0.0')