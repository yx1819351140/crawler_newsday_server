import subprocess
from scrapy import cmdline
from scrapy.utils.project import get_project_settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR


def run_spider(spider_name):
    subprocess.Popen(f"scrapy crawl {spider_name}", shell=True)


def create_job():
    spiders = get_project_settings().get('SPIDERS')
    sched = BlockingScheduler()
    for spider_name in spiders:
        trigger = spiders[spider_name]['trigger']
        month = spiders[spider_name]['month']
        day = spiders[spider_name]['day']
        hour = spiders[spider_name]['hour']
        minute = spiders[spider_name]['minute']
        # 添加任务
        sched.add_job(run_spider, trigger, month=month, day=day, hour=hour, minute=minute, args=[spider_name, ])
    return sched


def spider_listener(spider):
    if spider.exception:
        print('任务异常！')
    else:
        print('任务正常运行...')


def run():
    sched = create_job()
    # 配置任务执行完成和执行错误的监听
    sched.add_listener(spider_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    # 设置日志
    # sched._logger = logging
    # 开启任务
    sched.start()


if __name__ == '__main__':
    run()
    # run_spider('gma_news')
    # cmdline.execute("scrapy crawl gma_news".split())
