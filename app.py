from flask import Flask, send_from_directory, jsonify, request
from pprint import pprint
import dateutil.parser
import json
import redis
import requests
import validators


REDIS_ITEM_EXPIRE_TIME = 3600 * 24 * 7  # seconds
CLOJURE_APP = 'http://localhost:3000'


app = Flask(__name__, static_url_path='/static')


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


@app.route('/')
def index():
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


@app.route('/api/new-item/')
def get_new_items():
    new_items = sorted(get_new_items_redis(),
                       key=lambda x: dateutil.parser.parse(x['time']),
                       reverse=True)
    return jsonify({'items': new_items})


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


@app.route('/api/item/<item_id>/archive', methods=['POST'])
def archive(item_id):
    success = archive_item_redis(item_id)
    if success:
        print 'archive {}'.format(item_id)
        return jsonify({}), 204
    else:
        print 'fail'
        return jsonify({'error': 'cannot archive {}'.format(item_id)}), 500

if __name__ == '__main__':
    app.run(debug=True, host ='0.0.0.0')