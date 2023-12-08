# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings
from crawler_newsday_server.items import NewsItem
from crawler_newsday_server.utils.mongo_utils import MongoDB
import logging

logger = logging.getLogger(__name__)


class CrawlerNewsdayServerPipeline:

    def __init__(self):
        self.settings = get_project_settings()
        self.db = MongoDB()

    def process_item(self, item, spider):
        if item['news_title'] and item['news_content']:
            self.db.insert_data(self.settings.get('MONGO_TABLE'), dict(item))
            logger.info(f'insert data success!insert_id: {item["_id"]}')
        return item
