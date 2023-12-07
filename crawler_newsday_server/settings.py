# Scrapy settings for crawler_newsday_server project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

BOT_NAME = "crawler_newsday_server"

SPIDER_MODULES = ["crawler_newsday_server.spiders"]
NEWSPIDER_MODULE = "crawler_newsday_server.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "crawler_newsday_server (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "crawler_newsday_server.middlewares.CrawlerNewsdayServerSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "crawler_newsday_server.middlewares.CrawlerNewsdayServerDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "crawler_newsday_server.pipelines.CrawlerNewsdayServerPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# 日志级别
LOG_LEVEL = 'INFO'
LOG_FILE = 'crawler_newsday_server/log/scrapy.log'
LOG_ENCODING = "UTF-8"
# LOG_ENABLED = False
# Configure the TimedRotatingFileHandler
handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=5)
handler.setLevel(logging.DEBUG)
# Create a custom formatter
formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
# Configure the root logger
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.DEBUG)

# ERROR: HTTP status code is not handled or not allowed
HTTPERROR_ALLOWED_CODES = [301, 302]

# Mongo
# 本地
# MONGO_URL = '127.0.0.1'
# MONGO_DB = 'crawler_newsday'
# MONGO_TABLE = 'newsday_news'
# MONGO_PORT = 27017
# 远程
MONGO_URL = 'mongodb://news_crawler:5V^N-IRSwntAQ*9z9ZxGCAWGzBOZoH@52.1.169.11:7817/news_crawler_raw'
MONGO_DB = 'news_crawler_raw'
MONGO_TABLE = 'newsday_news'
MONGO_PORT = 27017

# 代理IP地址
PROXIES_HOST = {'http': '127.0.0.1:7890', 'https': '127.0.0.1:7890'}
PROXY = '127.0.0.1:7890'

# 失败重试
# 设置重试次数
RETRY_TIMES = 3
# 设置重试间隔时间
RETRY_BACKOFF_FACTOR = 2

# 任务管理
SPIDERS = {
    'gma_news': {'trigger': 'cron', 'month': '*', 'day': '*', 'hour': '*', 'minute': '7'},
}
