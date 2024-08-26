import re

from request_utils import get_page
from scrapy.selector import Selector

import datetime


def scrape_time(result_object):
    # Record the current time as scrape time
    now = datetime.datetime.now()
    result_object['scrape_time_str'] = now.strftime('%Y-%m-%d %H:%M:%S')
    result_object['scrape_timestamp'] = int(now.timestamp())
    return result_object


def review_page(page_text):
    page_selector = Selector(text=page_text)

    reviews = page_selector.css('.reviews-items > ul > li')
    if len(reviews) == 0:
        print('No reviews found. Exiting.')
        return None

    dianping_name = page_selector.css('h1.shop-name::text').get()

    results = []
    for review in reviews:
        # BUG: When call review.get, the whole following content is returned.
        # TODO: Add "like count" and "user rank" field.

        # Creating a result object
        result = {'dianping_name': dianping_name}

        result['text'] = ' '.join(review.css('.review-words::text').getall()).strip()

        # User link, name, ID
        user_name = review.css('.dper-info a::text').get()
        result['user_name'] = user_name.strip() if user_name else None

        user_link = review.css(':scope > a::attr(href)').get()
        if user_link:
            result['user_url'] = f'http://www.dianping.com{user_link}'
            result['user_id'] = user_link.split('/member/')[-1]

        # Iterate through Class to get rating
        rating_span = review.css('.review-rank span')
        if rating_span:
            for class_name in rating_span.css('::attr(class)').get().split(' '):
                if 'sml-str' in class_name:
                    result['rank'] = int(class_name.replace('sml-str', ''))
                    break

        # Directly getting bound images, no need to load images
        result['image_list'] = []
        for img in review.css('.review-pictures li'):
            img_url = img.css('a::attr(href)').get()
            thumbnail = img.css('img::attr(data-lazyload)').get()
            origin = img.css('img::attr(data-big)').get()
            result['image_list'].append({'url': img_url, 'thumbnail': thumbnail, 'origin': origin})

        # Get all emojis
        result['emoji_image_map'] = {}
        for emoji in review.css('.emoji-img'):
            emoji_src = emoji.css('::attr(src)').get()
            result['emoji_image_map'][emoji_src] = result['emoji_image_map'].get(emoji_src, 0) + 1

        # Publishing time, review link, ID
        publish_time = review.css('.time::text').get()
        result['publish_time'] = publish_time.strip() if publish_time else None

        review_link = review.css('.actions a::attr(href)').getall()[1].strip('//')
        result['url'] = review_link
        result['id'] = review_link.split('/review/')[-1]

        # Add the scrape time to the result object
        result = scrape_time(result)

        # Parse the publication time
        if '更新于' in result['publish_time']:
            result['first_time'], result['publish_time'] = result['publish_time'].split('更新于')
            result['first_time'] = result['first_time'].strip()

            # Convert 'first_time' to a timestamp
            try:
                first_time_obj = datetime.datetime.strptime(result['first_time'], '%Y-%m-%d')
                result['first_timestamp'] = int(first_time_obj.timestamp())
            except ValueError:
                result['first_timestamp'] = None

        # Convert 'publish_time' to a timestamp
        try:
            publish_time_obj = datetime.datetime.strptime(result['publish_time'].strip(), '%Y-%m-%d %H:%M')
            result['publish_timestamp'] = int(publish_time_obj.timestamp())
        except ValueError:
            result['publish_timestamp'] = None

        results.append(result)

    return results


def user_page(page_text):
    page_selector = Selector(text=page_text)

    result = {}

    # 用户ID
    url = page_selector.css('.nav .cur a::attr(href)').get()
    match = re.search(r'member/(\d+)', url)
    result["id"] = match.group(1) if match else None

    # 名称
    name = page_selector.css('h2.name::text').get()
    result["name"] = name if name else ""

    # 是否为VIP
    is_vip = page_selector.css('.icon-vip')
    result["is_vip"] = bool(is_vip)

    # 等级
    rank_element = page_selector.css('.user-info .user-rank-rst::attr(class)').get()
    rank = None
    if rank_element:
        for class_name in rank_element.split():
            if 'urr-rank' in class_name:
                # 目前网页有BUG，不显示等级。
                rank_str = class_name.replace('urr-rank', '')
                if rank_str == '':
                    rank = None
                else:
                    rank = int(rank_str)
                break
    result["rank"] = rank

    # 性别
    if page_selector.css('.woman'):
        result["gender"] = "woman"
    elif page_selector.css('.man'):
        result["gender"] = "man"
    else:
        result["gender"] = "unknown"

    # 城市
    city = page_selector.css('.user-groun::text').get()
    result["city"] = city if city else ""

    # 注册时间
    register_time = page_selector.css('.user-time').xpath('string(.)').get()
    if register_time:
        register_time = register_time.replace('注册时间：', '').strip()
    result["register_time"] = register_time if register_time else ""

    atten_list = page_selector.css('.user_atten strong::text').getall()
    attention = atten_list[0]
    fan = atten_list[1]
    like = atten_list[2]
    if attention.endswith('万'):
        attention = float(attention[:-1]) * 10000
    if fan.endswith('万'):
        fan = float(fan[:-1]) * 10000
    if like.endswith('万'):
        like = float(like[:-1]) * 10000
    result["attention"] = int(attention)
    result["fan"] = int(fan)
    result["like"] = int(like)

    return result


if __name__ == '__main__':
    page_text = get_page(
        'https://www.dianping.com/shop/G9K4MX4uAHO4TMjs/review_all/p2?queryType=sortType&queryVal=latest')
    review_page(page_text)
