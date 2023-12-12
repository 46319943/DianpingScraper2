import time

import request_utils
from page_extractor import review_page
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


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-i', '--id', help='Dianping ID', required=True)
    parser.add_argument('-n', '--name', help='Dianping Name', required=True)
    parser.add_argument('-p', '--page', help='Start Page', default=1, type=int)
    parser.add_argument('-d', '--database', help='Database Name', default='大众点评')
    parser.add_argument('-s', '--interval', help='Interval Seconds', default=10, type=int)
    parser.add_argument('-c', '--pool', help='Cookie Pool Size', default=1, type=int)

    args = parser.parse_args()

    request_utils.pool_size = args.pool

    client = MongoClient()
    db = client[args.database]
    scrape_review(args.id, args.name, args.page, args.interval)
