import subprocess
from crawler_newsday_server.settings import SPIDERS_TABLE
from apscheduler.schedulers.blocking import BlockingScheduler
from crawler_newsday_server.utils.mongo_utils import MongoDB


def run_spider(spider_name):
    print(f'run spider: {spider_name}')
    subprocess.Popen(f"scrapy crawl {spider_name}", shell=True)


def run():
    sched = BlockingScheduler()
    mongo = MongoDB()
    spider_list = mongo.db[SPIDERS_TABLE].find()
    for spider in spider_list:
        spider_name = spider['spider_name']
        trigger = spider['trigger']
        month = spider['month']
        day = spider['day']
        hour = spider['hour']
        minute = spider['minute']
        # 添加任务
        sched.add_job(run_spider, trigger, month=month, day=day, hour=hour, minute=minute, args=[spider_name, ])
    sched.start()


if __name__ == '__main__':
    run()
    # run_spider('rappler')
    # cmdline.execute("scrapy crawl philstar".split())
