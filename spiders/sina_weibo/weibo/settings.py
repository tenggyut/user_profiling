# -*- coding: utf-8 -*-
BOT_NAME = ['weibo']

SPIDER_MODULES = ['weibo']
NEWSPIDER_MODULE = 'weibo.spiders'

DOWNLOADER_MIDDLEWARES = {
    "weibo.middleware.UserAgentMiddleware": 401,
    "weibo.middleware.CookiesMiddleware": 402,
}
#ITEM_PIPELINES = ["Sina_spider2.pipelines.MongoDBPipleline"]
ITEM_PIPELINES = {'weibo.pipelines.JsonLinesExportPipeline': 1}

#SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
#SCHEDULER_PERSIST = True
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
#REDIE_URL = None
#REDIS_HOST = '192.168.1.199'
#REDIS_PORT = 6379

DOWNLOAD_DELAY = 2  # 间隔时间
#COMMANDS_MODULE = 'Sina_spider2.commands'
# LOG_LEVEL = 'INFO'  # 日志级别
# CONCURRENT_REQUESTS = 1
# CONCURRENT_ITEMS = 1
# CONCURRENT_REQUESTS_PER_IP = 1
