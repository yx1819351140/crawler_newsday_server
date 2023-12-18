from gne import GeneralNewsExtractor
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


class AbsCbnSpider(scrapy.Spider):
    name = "abs_cbn"
    # allowed_domains = ["abs-cbn.com"]
    # start_urls = ["https://abs-cbn.com"]
    mongo = MongoDB()
    logger = logging.getLogger(__name__)
    settings = get_project_settings()
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }
    catrgory_list = ['news', 'business', 'entertainment', 'life', 'sports', 'overseas', 'spotlight', 'weather', 'tv-patrol', 'dzmm', 'tfcnews', 'anc', 'ancx']

    def start_requests(self):
        for category in self.catrgory_list:
            page = 1
            url = f'https://news.abs-cbn.com/{category}?page={page}'
            yield Request(url, headers=self.headers, meta={'page': page}, callback=self.parse)

    def parse(self, response):
        try:
            page = response.meta['page']
            url_list = response.xpath('//div[@class="articles"]/article')
            for url in url_list:
                url = url.xpath('./a/@href').get()
                _id = md5_string(url)
                is_repeat = self.mongo.is_repeat(self.settings.get('MONGO_TABLE'), _id)
                if is_repeat:
                    self.logger.info(f'current news is repeat, url: {url}, _id: {_id}')
                    continue
                if url:
                    url = 'https://news.abs-cbn.com' + url
                    yield Request(url, headers=self.headers, callback=self.parse_detail)
            if page <= 5:
                page += 1
                url = response.url.split('?')[0] + f'?page={page}'
                yield Request(url, headers=self.headers, meta={'page': page}, callback=self.parse)
        except Exception as e:
            self.logger.error(f'parse list error, url: {response.url}, error: {e}')

    def parse_detail(self, response):
        try:
            title = response.xpath('//meta[@property="og:title"]/@content').get()
            content = ''
            html = etree.HTML(response.text)
            content_html_list = html.xpath('//*[@class="article-content" or @class="media-block video"]//p')
            for content_html in content_html_list:
                temp_content = ''.join(content_html.xpath('.//text()'))
                content = content + temp_content + '\n\n'
            content = content.strip()
            desc = response.xpath('//meta[@name="description"]/@content').get()
            author_name = response.xpath('//meta[@name="author"]/@content').get()
            head_pic = response.xpath('//meta[@property="og:image"]/@content').get()
            pub_time = response.xpath('//meta[@name="pubdate"]/@content').get().replace(
                'T', ' ')[:19]
            pub_timestamp = time_2_timestamp(pub_time)
            category = response.xpath('//meta[@name="category"]/@content').get()
            document = Document(response.text)
            news_content_html = document.summary(html_partial=True)
            item = NewsItem()
            _id = md5_string(response.url)
            item['_id'] = _id
            item['news_id'] = 'crawler_' + _id
            item['news_url'] = response.url
            item['news_title'] = title
            item['news_description'] = desc
            item['news_content'] = content
            item['news_content_html'] = news_content_html
            item['news_publish_timestamp'] = pub_timestamp
            item['news_publish_time'] = time_2_isotime(pub_time)
            item['news_head_pic'] = head_pic
            item['news_source'] = 'abs_cbn'
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
