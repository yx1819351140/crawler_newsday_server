import json
from lxml import etree
import requests
import scrapy
from scrapy import Request
from scrapy.utils.project import get_project_settings
from crawler_newsday_server.utils.common_utils import md5_string
from crawler_newsday_server.utils.mongo_utils import MongoDB
from crawler_newsday_server.utils.date_utils import time_2_timestamp, time_2_isotime
from crawler_newsday_server.items import NewsItem
import logging
import time
from readability import Document
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class GmaNewsSpider(scrapy.Spider):
    name = "gma_news"
    # allowed_domains = ["gmanetwork.com"]
    # start_urls = ["https://gmanetwork.com"]
    mongo = MongoDB()
    category_list = {
        'story_news': 7830,
        'story_money': 1750,
        'story_sports': 1800,
        'story_pinoyabroad': 399,
        'story_showbiz': 1354,
        'story_lifestyle': 1079,
        'story_opinion': 65,
        'story_hashtag': 207,
        'story_serbisyopubliko': 29,
        'story_cbb': 75,
    }
    url = 'https://data2.gmanetwork.com/gno/widgets/grid_reverse_listing/{}/{}.gz'
    logger = logging.getLogger(__name__)
    settings = get_project_settings()
    retry_times = settings.get("RETRY_TIMES")
    retry_backoff_factor = settings.get("RETRY_BACKOFF_FACTOR")
    proxies_host = settings.get('PROXIES_HOST')

    def start_requests(self):
        for category, category_id in self.category_list.items():
            for i in range(5):
                url = self.url.format(category, category_id - i)
                yield Request(url, meta={'category': category, 'category_id': category_id}, callback=self.parse)

    def parse(self, response):
        data_list = json.loads(response.text).get('data', [])
        if data_list:
            for data in data_list:
                item = NewsItem()
                url = 'https://www.gmanetwork.com/news/' + data.get('article_url', '')
                _id = md5_string(url)
                is_repeat = self.mongo.is_repeat(self.settings.get('MONGO_TABLE'), _id)
                if is_repeat:
                    self.logger.info(f'current news is repeat, url: {url}, _id: {_id}')
                    continue
                item['_id'] = _id
                item['news_id'] = 'crawler_' + _id
                item['news_url'] = url
                item['news_title'] = data.get('title', '')
                item['news_description'] = data.get('lead', '')
                item['news_content'], item['news_content_html'] = self.get_content(item['news_url'])
                item['news_publish_time'] = time_2_isotime(data.get('publish_timestamp', ''))
                item['news_publish_timestamp'] = time_2_timestamp(data.get('publish_timestamp', ''))
                item['news_head_pic'] = data.get('photo', {}).get('base_url', '') + data.get('photo', {}).get(
                    'image_filename', '')
                item['news_source'] = 'GMA News'
                item['news_category'] = data.get('section', {}).get('sec_name', '')
                item['news_language'] = 'en'
                item['news_country'] = 'ph'
                item['news_author_dict'] = {'author_name': data.get('author', ''), 'channel_name': '', 'author_img': ''}
                item['news_status'] = 'active'
                item['news_stat_dict'] = {"clicks": 0}
                item['news_crawler'] = 'local_crawler'
                item['related_news'] = []
                item['create_time'] = time_2_isotime(time.strftime('%Y-%m-%d %H:%M:%S'))
                item['update_time'] = time_2_isotime(time.strftime('%Y-%m-%d %H:%M:%S'))
                yield item

    def get_content(self, url):
        try:
            session = requests.Session()
            retry = Retry(total=self.retry_times, backoff_factor=self.retry_backoff_factor,
                          status_forcelist=[404, 443, 500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            # 本地调试，添加代理
            # res = session.get(url, proxies=self.proxies_host)
            # 国外服务器，暂时不添加代理
            res = session.get(url)
            document = Document(res.text)
            news_content_html = document.summary(html_partial=True)
            html = etree.HTML(res.text)
            content_html_list = html.xpath('//div[@class="story_main"]/p')
            news_content = ''
            for content_html in content_html_list:
                temp_content = ''.join(content_html.xpath('.//text()'))
                news_content = news_content + temp_content + '\n\n'
            return news_content.strip(), news_content_html
        except Exception as e:
            self.logger.error(f'get news content failed, url: {url}, error: {e}')
            return '', ''
