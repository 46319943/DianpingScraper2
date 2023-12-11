import time

from page_extractor import review_page
from request_utils import get_page
from pymongo import MongoClient

client = MongoClient()
db = client['五感']


def scrape_review(dianping_id, dianping_name, start_page=1):
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
        time.sleep(5)


scrape_review('G9K4MX4uAHO4TMjs', '拙政园', start_page=54)
