from datetime import datetime
from gne import GeneralNewsExtractor
from lxml import etree
from readability import Document
import scrapy
from scrapy import Request
from scrapy.utils.project import get_project_settings
from crawler_newsday_server.utils.common_utils import md5_string
from crawler_newsday_server.utils.mongo_utils import MongoDB
from crawler_newsday_server.utils.date_utils import timestamp_2_time, time_2_timestamp, time_2_isotime, convert_to_beijing_time
from crawler_newsday_server.items import NewsItem
import logging


class SunstarSpider(scrapy.Spider):
    name = "sunstar"
    # allowed_domains = ["sunstar.com"]
    # start_urls = ["https://sunstar.com"]
    mongo = MongoDB()
    logger = logging.getLogger(__name__)
    settings = get_project_settings()
    category_list = ['bacolod', 'cdo', 'cebu', 'davao', 'iloilo', 'pampanga', 'tacloban', 'zamboanga', 'superbalitacebu', 'superbalitadavao']

    def start_requests(self):
        for category in self.category_list:
            for page in range(5):
                url = f'https://www.sunstar.com.ph/api/v1/collections/{category}-top-stories?item-type=story&offset={page*16}&limit=16'
                yield Request(url, meta={'category': category}, callback=self.parse)

    def parse(self, response):
        try:
            item_list = response.json().get('items', [])
            for item in item_list:
                data = item.get('story', {})
                _id = md5_string(data.get('url', ''))
                is_repeat = self.mongo.is_repeat(self.settings.get('MONGO_TABLE'), _id)
                if is_repeat:
                    self.logger.info(f'current news is repeat, url: {data.get("url", "")}, _id: {_id}')
                    continue
                else:
                    category = response.meta['category']
                    yield Request(data.get('url', ''), meta={'category': category}, callback=self.parse_detail)
        except Exception as e:
            self.logger.error(f'parse index error, url: {response.url}, error: {e}')

    def parse_detail(self, response):
        try:
            _id = md5_string(response.url)
            try:
                title = response.xpath('//meta[@name="twitter:title"]/@content').get()
            except:
                title = ''
            try:
                content = ''
                html = etree.HTML(response.text)
                content_html_list = html.xpath('//div[@data-test-id="text"]/p')
                for content_html in content_html_list:
                    temp_content = ''.join(content_html.xpath('.//text()'))
                    content = content + temp_content + '\n\n'
                content = content.strip()
            except:
                extractor = GeneralNewsExtractor()
                content = extractor.extract(html=response.text, with_body_html=True)['content']
            if title and content:
                document = Document(response.text)
                news_content_html = document.summary(html_partial=True)
                description = ''
                try:
                    description = response.xpath('//meta[@property="og:description"]/@content').get()
                except:
                    pass
                publish_time = response.xpath('//time[@class="arr__timeago"]/text()').get()
                publish_time = datetime.strptime(publish_time, "%b %d, %Y, %I:%M %p").strftime('%Y-%m-%d %H:%M:%S')
                publish_timestamp = time_2_timestamp(publish_time)
                try:
                    head_pic = response.xpath('//meta[@property="og:image"]/@content').get()
                except:
                    head_pic = ''
                try:
                    author_name = response.xpath('//meta[@name="author"]/@content').get()
                except:
                    author_name = ''
                category = response.meta['category']

                item = NewsItem()
                item['_id'] = _id
                item['news_id'] = 'crawler_' + _id
                item['news_url'] = response.url
                item['news_title'] = title
                item['news_description'] = description
                item['news_content'] = content
                item['news_content_html'] = news_content_html
                item['news_publish_time'] = time_2_isotime(publish_time)
                item['news_publish_timestamp'] = publish_timestamp
                item['news_head_pic'] = head_pic
                item['news_source'] = 'sunstar'
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
            self.logger.error(f'parse detail error, url: {response.url}, error: {e}')
