import scrapy
from readability import Document
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


class PhilstarSpider(scrapy.Spider):
    name = "philstar"
    # allowed_domains = ["philstar.com"]
    start_urls = ["https://www.philstar.com/other-sections"]
    mongo = MongoDB()
    logger = logging.getLogger(__name__)
    settings = get_project_settings()

    def parse(self, response):
        try:
            url_list = response.xpath('//div[@class="theContent"]/div[1]//a/@href').getall()
            for url in url_list:
                yield Request(url, meta={'page': 1}, callback=self.parse_list)
        except Exception as e:
            self.logger.error(f'parse index error, url: {response.url}, error: {e}')

    def parse_list(self, response):
        try:
            url_list = response.xpath('//div[@class="microsite_article_title" or @class="news_title"]/h2/a/@href').getall()
            for url in url_list:
                _id = md5_string(url)
                is_repeat = self.mongo.is_repeat(self.settings.get('MONGO_TABLE'), _id)
                if is_repeat:
                    self.logger.info(f'current news is repeat, url: {url}, _id: {_id}')
                    continue
                yield Request(url, callback=self.parse_detail)
            page = response.meta['page']
            nxt_url = response.xpath('//div[@class="next"]/a/@href').get()
            if page <= 5 and nxt_url:
                page += 1
                yield Request(nxt_url, meta={'page': page}, callback=self.parse_list)
        except Exception as e:
            self.logger.error(f'parse list error, url: {response.url}, error: {e}')

    def parse_detail(self, response):
        try:
            news_data = json.loads(response.xpath('//script[@type="application/ld+json"]/text()').get())
            title = news_data.get('headline', '')
            desc = news_data.get('description', '')
            publish_time = news_data.get('datePublished', '').replace('T', ' ')[0:19]
            try:
                head_pic = news_data.get('image', [])[0]
            except:
                head_pic = ''
            author_name = news_data.get('author', {}).get('name', '')
            category = news_data.get('articleSection', '')
            try:
                content = ''
                html = etree.HTML(response.text)
                content_html_list = html.xpath('//div[@id="sports_article_writeup"]/p')
                for content_html in content_html_list:
                    temp_content = ''.join(content_html.xpath('.//text()'))
                    content = content + temp_content + '\n\n'
                content = content.strip()
            except:
                content = ''
            document = Document(response.text)
            news_content_html = document.summary(html_partial=True)

            _id = md5_string(response.url)
            item = NewsItem()
            item['_id'] = _id
            item['news_id'] = 'crawler_' + _id
            item['news_url'] = response.url
            item['news_title'] = title
            item['news_description'] = desc
            item['news_content'] = content
            item['news_content_html'] = news_content_html
            item['news_publish_time'] = publish_time
            item['news_publish_timestamp'] = time_2_timestamp(item['news_publish_time'])
            item['news_publish_time'] = time_2_isotime(item['news_publish_time'])
            item['news_head_pic'] = head_pic
            item['news_source'] = 'philstar'
            item['news_category'] = category
            item['news_language'] = 'en'
            item['news_country'] = 'ph'
            item['news_author_dict'] = {'author_name': author_name, 'channel_name': '', 'author_img': ''}
            item['news_status'] = 'active'
            item['news_stat_dict'] = {"clicks": 0}
            item['news_crawler'] = 'local_crawler'
            item['related_news'] = []
            item['create_time'] = time_2_isotime(convert_to_beijing_time())
            item['update_time'] = time_2_isotime(convert_to_beijing_time())
            # print(dict(item))
            yield item
        except Exception as e:
            self.logger.error(f'get news content failed, url: {response.url}, error: {e}')
