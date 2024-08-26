# DianpingScraper Version 2
The second version of the DianpingScraper. The first version can be found [here](https://github.com/46319943/DianpingScraper)  

The **DianpingScraper** is a scraper for the Chinese restaurant review website [大众点评](http://www.dianping.com/). It is designed to scrape the reviews of a restaurant, and store the data in a MongoDB database.

# Change of the version 2.
- OCR module is removed from the version 1, since the text is no longer encrypted using the css font.
- The subsequent analytical steps are removed, as this is just a scraper. The further analysis should be done separately.

# Prerequisites
- MongoDB
- Nodejs
- Python

# Quick start
- Clone the repository  
`git clone https://github.com/46319943/DianpingScraper2.git`
- Install the requirements for python  
`pip install -r requirements.txt`
- Go to the CookieServer folder and install the requirements for nodejs  
`cd CookieServer`  
`npm install`
- Run the cookie server  
`node Server.js`
- Return to the root folder of the project and Run the `pipeline_manager.py` with arguments  
`python pipeline_manager.py -i <大众点评的ID> -n <大众点评的名称> [-p <开始页面数>] [-d <数据库名称>]`
- For example, to scrape the reviews of the restaurant [拙政园](http://www.dianping.com/shop/G9K4MX4uAHO4TMjs) from page 1, and store the data in the database `苏州园林`, run the following command:  
`python pipeline_manager.py -i G9K4MX4uAHO4TMjs -n 拙政园 -p 1 -d 苏州园林`
- The data will be stored in the MongoDB database. To export the data, run the following command:  
`python export_to_json.py -d <数据库名称> [-c <大众点评的名称>]`

## Call with python
```python
from pipeline_manager import scrape_review_wrapper

cookie_pool_size = 1
database_name = '苏州园林'
dianping_id = 'G9K4MX4uAHO4TMjs'
dianping_name = '拙政园'
start_page = 1
interval_seconds = 10
scrape_review_wrapper(cookie_pool_size, database_name, dianping_id, dianping_name, start_page, interval_seconds)
```



# Sample Result
```
{
  "_id": {
    "$oid": "657717bbdbd195d536fd6e4d"
  },
  "id": "1530835160",
  "dianping_name": "拙政园",
  "emoji_image_map": {},
  "image_list": [
    {
      "url": "/photos/4476037337",
      "thumbnail": "https://qcloud.dpfile.com/pc/tZt7kjZ_ElqENZNMDpxG-QKJo1O3uFHzo1o-K65ujhp7OD79kdPJO7Nqv49mcO_GUBBCaBtJvKU_sxCtKYAYUQ.jpg",
      "origin": "https://qcloud.dpfile.com/pc/tZt7kjZ_ElqENZNMDpxG-QKJo1O3uFHzo1o-K65ujhrU3SC5nxN0XdtGwXSP-AT1joJrvItByyS4HHaWdXyO_I7F0UeCRQYMHlogzbt7GHgNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg"
    },
    {
      "url": "/photos/4476042072",
      "thumbnail": "https://qcloud.dpfile.com/pc/6eGX4LSsuL5qbyTn64cfh1i43f0ipfxp2iFH1JNyoAhBq545Al4KXLLXjGW5U2cvUBBCaBtJvKU_sxCtKYAYUQ.jpg",
      "origin": "https://qcloud.dpfile.com/pc/6eGX4LSsuL5qbyTn64cfh1i43f0ipfxp2iFH1JNyoAhdo_J2BOAVauavBqpBqhsJjoJrvItByyS4HHaWdXyO_I7F0UeCRQYMHlogzbt7GHgNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg"
    }
  ],
  "publish_time": "2023-12-11 21:57",
  "publish_timestamp": 1702303020,
  "rank": 50,
  "scrape_time_str": "2023-12-11 22:15:05",
  "scrape_timestamp": 1702304105,
  "text": "感觉是苏州必去的一个园林 面积很大\n平时周末人也好多！很难拍出好看的照片\n建议刚开园就去！园林景观 曲曲折折的路\n秋天去的枫叶很红！太多人拍照了 \n一定要在大众点评买门票 其他平台没有\n还能送一张盖章的明信片  在快要出口的文创店",
  "url": "www.dianping.com/review/1530835160",
  "user_id": "1352049205",
  "user_name": "样妹",
  "user_url": "http://www.dianping.com/member/1352049205"
}
```