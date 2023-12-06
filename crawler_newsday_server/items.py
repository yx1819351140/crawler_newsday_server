# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GmaNewsItem(scrapy.Item):
    _id = scrapy.Field()
    news_id = scrapy.Field()
    news_title = scrapy.Field()
    news_description = scrapy.Field()
    news_url = scrapy.Field()
    news_content = scrapy.Field()
    news_content_html = scrapy.Field()
    news_publish_time = scrapy.Field()
    news_publish_timestamp = scrapy.Field()
    news_head_pic = scrapy.Field()
    news_source = scrapy.Field()
    news_category = scrapy.Field()
    news_language = scrapy.Field()
    news_country = scrapy.Field()
    news_author_dict = scrapy.Field()
    news_status = scrapy.Field()
    news_stat_dict = scrapy.Field()
    news_crawler = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
