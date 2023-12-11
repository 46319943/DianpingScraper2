from requests import get


def get_cookie():
    return get('http://localhost:3001/').text


cookie_text = get_cookie()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'

proxies = {
    "http": "",
    "https": "",
}


def get_page(url):
    res = get(url,
              proxies=proxies,
              headers={'Cookie': cookie_text, 'Referer': 'http://www.dianping.com/', 'User-Agent': user_agent})
    if res.status_code == 403:
        # Re-login is required to refresh the cookie.
        print('403 Forbidden')

    text = res.text
    text = text.replace('<!-- ok-->', ' ')

    return text


if __name__ == '__main__':
    get_page('https://www.dianping.com/shop/G9K4MX4uAHO4TMjs/review_all/p2?queryType=sortType&queryVal=latest')
    pass
