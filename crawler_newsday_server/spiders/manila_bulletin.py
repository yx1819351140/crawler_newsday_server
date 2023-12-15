import scrapy
from scrapy import Request
from scrapy.utils.project import get_project_settings
from crawler_newsday_server.utils.common_utils import md5_string
from crawler_newsday_server.utils.mongo_utils import MongoDB
from crawler_newsday_server.utils.date_utils import time_2_timestamp, time_2_isotime, convert_to_beijing_time
from crawler_newsday_server.items import NewsItem
from lxml import etree
import logging
import time
import json


class ManilaBulletinSpider(scrapy.Spider):
    name = "manila_bulletin"
    # allowed_domains = ["mb.com"]
    # start_urls = ["https://mb.com"]
    mongo = MongoDB()
    logger = logging.getLogger(__name__)
    settings = get_project_settings()
    category_list = {
        'news': 'news',
        'business': 'bussiness',
        'economics': 'economic-and-utilities',
        'opinion': 'opinion',
        'entertainment': 'entertainment',
        'sports': 'sports',
        'technology': 'technology',
        'lifestyle': 'lifestyle',
        'specials': 'specials'
    }
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    url = 'https://admin.mb.com.ph/api/articles?filters[$or][0][categories][slug][$in][0]={}&filters[$or][1][category_primary][slug][$in][0]={}&sort[0]=publishedAt%3Adesc&populate[0]=featured_image&populate[1]=author&populate[2]=categories&populate[3]=category_primary&populate[4]=tags&pagination[page]={}&pagination[pageSize]=20'

    def start_requests(self):
        for catrgory in self.category_list:
            for page in range(1, 5):
                url = self.url.format(catrgory, catrgory, page)
                yield Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        try:
            data_list = json.loads(response.text).get('data', [])
            if data_list:
                for data in data_list:
                    item = NewsItem()
                    data = data.get('attributes')
                    url = 'https://mb.com.ph/' + data.get('publishedAt', '')[:10].replace('-', '/') + '/' + data.get('slug', '')
                    _id = md5_string(url)
                    is_repeat = self.mongo.is_repeat(self.settings.get('MONGO_TABLE'), _id)
                    if is_repeat:
                        self.logger.info(f'current news is repeat, url: {url}, _id: {_id}')
                        continue
                    item['_id'] = _id
                    item['news_id'] = 'crawler_' + _id
                    item['news_url'] = url
                    item['news_title'] = data.get('title', '')
                    content = ''
                    html = etree.HTML(data.get('body', ''))
                    content_html_list = html.xpath('//p')
                    for content_html in content_html_list:
                        temp_content = ''.join(content_html.xpath('.//text()'))
                        content = content + temp_content + '\n\n'
                    content = content.replace('\xa0', '').strip()
                    item['news_content'] = content
                    item['news_content_html'] = data.get('body', '')
                    item['news_description'] = data.get('excerpt', '').replace('<p>', '').replace('</p>', '')
                    item['news_publish_time'] = data.get('publishedAt', '').replace('T', ' ')[:19]
                    item['news_publish_timestamp'] = time_2_timestamp(item['news_publish_time'])
                    item['news_publish_time'] = time_2_isotime(item['news_publish_time'])
                    item['news_head_pic'] = data.get('featured_image', {}).get('data', {}).get('attributes', {}).get('url', '')
                    item['news_source'] = 'manila_bulletin'
                    item['news_category'] = data.get('categories', {}).get('data')[0].get('attributes', '').get('name', '')
                    item['news_language'] = 'en'
                    item['news_country'] = 'PH'
                    item['news_author_dict'] = {
                        'author_name': data.get('author', {}).get('data', {}).get('attributes', {}).get('name', ''), 'channel_name': '', 'author_img': ''
                    }
                    item['news_status'] = 0
                    item['news_stat_dict'] = {
                        "clicks": 0
                    }
                    item['news_crawler'] = 'local_crawler'
                    item['related_news'] = []
                    item['create_time'] = time_2_isotime(convert_to_beijing_time())
                    item['update_time'] = time_2_isotime(convert_to_beijing_time())
                    yield item
        except Exception as e:
            self.logger.error(f'get news content failed, url: {response.url}, error: {e}')
