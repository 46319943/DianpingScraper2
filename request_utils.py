from requests import get
from pymongo import MongoClient

client = MongoClient()
db = client['大众点评']
collection = db['CookiePool']

pool_size = 1

def add_cookie():
    new_cookie = get('http://localhost:3001').text
    collection.insert_one({'cookie': new_cookie})


def get_cookie():
    while collection.count_documents({}) < pool_size:
        add_cookie()

    # Randomly get a cookie from the pool.
    cookie = collection.aggregate([{'$sample': {'size': 1}}]).next()['cookie']
    return cookie


def delete_cookie(cookie):
    collection.delete_one({'cookie': cookie})


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'

proxies = {
    "http": "",
    "https": "",
}


def get_page(url):
    cookie = get_cookie()
    res = get(url,
              proxies=proxies,
              headers={'Cookie': cookie, 'Referer': 'http://www.dianping.com/', 'User-Agent': user_agent})
    if res.status_code == 403:
        # Re-login is required to refresh the cookie.
        delete_cookie(cookie)
        return get_page(url)
    if '<span class="sub-logo">登录</span>' in res.text:
        # Re-login is required to refresh the cookie.
        delete_cookie(cookie)
        return get_page(url)

    text = res.text
    text = text.replace('<!-- ok-->', ' ')

    return text


if __name__ == '__main__':
    get_page('https://www.dianping.com/shop/G9K4MX4uAHO4TMjs/review_all/p2?queryType=sortType&queryVal=latest')
    pass
