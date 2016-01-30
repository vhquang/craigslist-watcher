import json, os, subprocess
import redis
import gcm


REDIS_ITEM_EXPIRE_TIME = 3600 * 24 * 7  # seconds

config = json.load(open('config.json', 'r'))
DEVICE_TOKEN = config['device_token']
GCM_API_KEY = config['gcm_api_key']

def scrap_page(link, item_name):
    file_name = '{}.json'.format(item_name)
    subprocess.call(['phantomjs',
                     '--ignore-ssl-errors=true', '--web-security=no',
                     '--ssl-protocol=tlsv1',
                     'scrap_clist.js', link, file_name])
    return file_name


def gcm_notify(device_token, message):
    data = {'message': message}
    gcm_client = gcm.GCM(GCM_API_KEY)
    resp = gcm_client.json_request(registration_ids=[device_token],data=data)
                                   # collapse_key='nexus', delay_while_idle=False
    if 'success' not in resp or not resp['success']:
        print resp


def update_database(data):
    redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)
    for _id, item in data.iteritems():
        key_old_item = 'old:item:{}'.format(_id)
        key_new_item = 'new:item:{}'.format(_id)
        if item['price'] != redis_db.hget(key_old_item, 'price'):
            redis_db.delete(key_old_item)
            redis_db.hmset(key_new_item, item)
            redis_db.expire(key_new_item, REDIS_ITEM_EXPIRE_TIME)
            gcm_notify(DEVICE_TOKEN, item['title'])


def watch_craigslist(link, item_name):
    file_name = scrap_page(link, item_name)
    data = json.load(open(file_name, 'r'))
    update_database(data)
    os.remove(file_name)


def main():
    pass


if __name__ == '__main__':
    main()
