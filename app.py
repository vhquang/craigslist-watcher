from flask import Flask, send_from_directory, jsonify
import dateutil.parser
import redis

EXPIRE_TIME = 3600 * 24 * 7  # seconds


app = Flask(__name__, static_url_path='/static')


def get_new_items_redis():
    redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)
    new_item_keys = redis_db.keys('new:item:*')
    res = [redis_db.hgetall(key) for key in new_item_keys]
    return res


def archive_item_redis(item_id):
    redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)
    new_item_key = 'new:item:{}'.format(item_id)
    old_item_key = 'old:item:{}'.format(item_id)
    return redis_db.renamenx(new_item_key, old_item_key)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/<path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/api/new-item/')
def get_new_items():
    new_items = sorted(get_new_items_redis(),
                       key=lambda x: dateutil.parser.parse(x['time']),
                       reverse=True)
    return jsonify({'items': new_items})


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