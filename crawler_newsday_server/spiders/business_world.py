from gne import GeneralNewsExtractor
from lxml import etree
from readability import Document
import scrapy
from scrapy import Request
from scrapy.utils.project import get_project_settings
from crawler_newsday_server.utils.common_utils import md5_string
from crawler_newsday_server.utils.mongo_utils import MongoDB
from crawler_newsday_server.utils.date_utils import time_2_timestamp, time_2_isotime, pst_2_strftime, convert_to_beijing_time
from crawler_newsday_server.items import NewsItem
import logging
import time


class BusinessWorldSpider(scrapy.Spider):
    name = "business_world"
    # allowed_domains = ["bworldonline.com"]
    # start_urls = ["https://bworldonline.com"]
    mongo = MongoDB()
    logger = logging.getLogger(__name__)
    settings = get_project_settings()
    category_list = ['corporate', 'stock-market', 'banking-finance', 'economy', 'markets', 'the-nation', 'world', 'opinion', 'infographics', 'podcast', 'sparkup', 'spotlight', 'labor-and-management', 'property', 'agribusiness', 'health', 'arts-and-leisure', 'technology', 'velocity', 'special-features', 'sports', 'special-reports', 'bw-launchpad']

    def start_requests(self):
        for category in self.category_list:
            for page in range(1, 6):
                url = f'https://bworldonline.com/{category}/page/{page}/'
                yield Request(url, meta={'category': category}, callback=self.parse)

    def parse(self, response):
        try:
            url_list = response.xpath('//div[@class="item-details"]/h3/a/@href').getall()
            for url in url_list:
                _id = md5_string(url)
                is_repeat = self.mongo.is_repeat(self.settings.get('MONGO_TABLE'), _id)
                if is_repeat:
                    self.logger.info(f'current news is repeat, url: {url}, _id: {_id}')
                    continue
                else:
                    category = response.meta['category']
                    yield Request(url, meta={'category': category}, callback=self.parse_detail)
        except Exception as e:
            self.logger.error(f'parse list page failed, error: {e}')

    def parse_detail(self, response):
        try:
            _id = md5_string(response.url)
            try:
                title = response.xpath('//meta[@property="og:title"]/@content').get()
            except:
                title = ''
            try:
                content = ''
                html = etree.HTML(response.text)
                content_html_list = html.xpath('//div[@class="td-post-content td-pb-padding-side"]/p')
                for content_html in content_html_list:
                    temp_content = ''.join(content_html.xpath('.//text()'))
                    content = content + temp_content + '\n\n'
                content = content.strip()
            except:
                extractor = GeneralNewsExtractor()
                content = extractor.extract(html=response.text, with_body_html=True)['content']
            if title and content:
                try:
                    description = response.xpath('//meta[@property="og:description"]/@content').get()
                except:
                    description = ''
                try:
                    publish_time = response.xpath('//meta[@property="article:published_time"]/@content').get().replace(
                        'T', ' ')[:19]
                    publish_timestamp = time_2_timestamp(publish_time)
                    publish_time = time_2_isotime(publish_time)
                except:
                    publish_time = ''
                    publish_timestamp = ''
                try:
                    author_name = response.xpath('//meta[@name="author"]/@content').get()
                except:
                    author_name = ''
                try:
                    head_pic = response.xpath('//meta[@property="og:image"]/@content').get()
                except:
                    head_pic = ''
                try:
                    document = Document(response.text)
                    news_content_html = document.summary(html_partial=True)
                except:
                    news_content_html = ''

                item = NewsItem()
                item['_id'] = _id
                item['news_id'] = 'crawler_' + _id
                item['news_url'] = response.url
                item['news_title'] = title.replace('\xa0', '')
                item['news_description'] = description
                item['news_content'] = content
                item['news_content_html'] = news_content_html
                item['news_publish_time'] = publish_time
                item['news_publish_timestamp'] = publish_timestamp
                item['news_head_pic'] = head_pic
                item['news_source'] = 'business_world'
                item['news_category'] = response.meta['category']
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
