import subprocess
from crawler_newsday_server.settings import SPIDERS
from apscheduler.schedulers.blocking import BlockingScheduler


def run_spider(spider_name):
    print(f'run spider: {spider_name}')
    subprocess.Popen(f"scrapy crawl {spider_name}", shell=True)


def run():
    sched = BlockingScheduler()
    for spider_name in SPIDERS:
        trigger = SPIDERS[spider_name]['trigger']
        month = SPIDERS[spider_name]['month']
        day = SPIDERS[spider_name]['day']
        hour = SPIDERS[spider_name]['hour']
        minute = SPIDERS[spider_name]['minute']
        # 添加任务
        sched.add_job(run_spider, trigger, month=month, day=day, hour=hour, minute=minute, args=[spider_name, ])
    sched.start()


if __name__ == '__main__':
    run()
    # run_spider('rappler')
    # cmdline.execute("scrapy crawl philstar".split())
