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
        print('No reviews.')
        return None

    dianping_name = page_selector.css('h1.shop-name::text').get()

    results = []
    for review in reviews:
        # BUG: When call review.get, the whole following content is returned.

        # Creating a result object
        result = {'dianping_name': dianping_name}

        result['text'] = review.css('.review-words::text').get().strip()

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


if __name__ == '__main__':
    page_text = get_page(
        'https://www.dianping.com/shop/G9K4MX4uAHO4TMjs/review_all/p2?queryType=sortType&queryVal=latest')
    review_page(page_text)
