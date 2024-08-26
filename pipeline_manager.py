import time

import request_utils
from requests import get
from page_extractor import review_page, user_page
from request_utils import get_page
from pymongo import MongoClient

from argparse import ArgumentParser


def scrape_review(dianping_id, dianping_name, start_page, interval_seconds):
    page = start_page
    collection = db[dianping_name]

    while True:
        print(f'Scraping page {page}...')

        page_text = get_page(
            f'https://www.dianping.com/shop/{dianping_id}/review_all/p{page}?queryType=sortType&queryVal=latest')
        results = review_page(page_text)

        if not results:
            break

        # Insert the results. Update the existing ones.
        for result in results:
            collection.update_one({'id': result['id']}, {'$set': result}, upsert=True)

        page += 1

        # wait for some seconds
        time.sleep(interval_seconds)


def scrape_review_wrapper(cookie_pool_size, database_name, dianping_id, dianping_name, start_page, interval_seconds):
    global db
    request_utils.pool_size = cookie_pool_size
    db = MongoClient()[database_name]
    scrape_review(dianping_id, dianping_name, start_page, interval_seconds)


def scrape_user(user_id):
    collection = db['users']
    page_text = get_page(
        f'https://www.dianping.com/member/{user_id}')
    result = user_page(page_text)
    collection.update_one({'id': result['id']}, {'$set': result}, upsert=True)


def scrape_user_in_db():
    # Get all collections in the database.
    collections = db.list_collection_names()
    user_collection = 'usersCard'

    # Get all the user IDs.
    user_ids = []
    for collection_name in collections:
        if collection_name == user_collection:
            continue
        for review in db[collection_name].find():
            if 'user_id' in review:
                user_ids.append(review['user_id'])

    # Remove the duplicates.
    user_ids = list(set(user_ids))

    # Get all the user IDs in the database.
    user_ids_in_db = []
    for user in db[user_collection].find():
        user_ids_in_db.append(user['id'])

    # Remove the user IDs that are already in the database.
    user_ids = list(set(user_ids) - set(user_ids_in_db))

    # Print the count of existing and new user IDs.
    print(f'Existing User IDs: {len(user_ids_in_db)}')
    print(f'New User IDs: {len(user_ids)}')

    # Scrape the user information.
    for user_id in user_ids:
        # scrape_user(user_id)
        USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'
        response = get(f'https://www.dianping.com/ajax/json/shopDynamic/userCardData?userId={user_id}',
                       headers={'User-Agent': USER_AGENT})
        while response.status_code != 200:
            print(f'Failed to get user information for user ID {user_id}. Retrying in 5 seconds...')
            time.sleep(5)
            response = get(f'https://www.dianping.com/ajax/json/shopDynamic/userCardData?userId={user_id}',
                           headers={'User-Agent': USER_AGENT})
        result = response.json()
        if result['code'] == 200:
            result = result['msg']['userCarte']
            result['id'] = user_id
            db[user_collection].update_one({'id': result['id']}, {'$set': result}, upsert=True)
        else:
            raise Exception(f'Failed to get user information for user ID {user_id}.')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-i', '--id', help='Dianping ID', required=True)
    parser.add_argument('-n', '--name', help='Dianping Name', required=True)
    parser.add_argument('-p', '--page', help='Start Page', default=1, type=int)
    parser.add_argument('-d', '--database', help='Database Name', default='大众点评')
    parser.add_argument('-s', '--interval', help='Interval Seconds', default=10, type=int)
    parser.add_argument('-c', '--pool', help='Cookie Pool Size', default=1, type=int)
    parser.add_argument('-u', '--user', help='Scrape User', action='store_true', default=False)

    args = parser.parse_args()

    request_utils.pool_size = args.pool

    client = MongoClient()
    db = client[args.database]
    if args.user:
        scrape_user_in_db()
    else:
        scrape_review(args.id, args.name, args.page, args.interval)
