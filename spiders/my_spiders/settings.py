# -*- coding: utf-8 -*-
BOT_NAME = ['my_spiders']

SPIDER_MODULES = ['my_spiders']
NEWSPIDER_MODULE = 'my_spiders.spiders'

DOWNLOADER_MIDDLEWARES = {
    "my_spiders.middleware.UserAgentMiddleware": 401,
    "my_spiders.middleware.CookiesMiddleware": 402,
}
#ITEM_PIPELINES = ["Sina_spider2.pipelines.MongoDBPipleline"]
#ITEM_PIPELINES = {'my_spiders.pipelines.JsonLinesExportPipeline': 1}
ITEM_PIPELINES = {'my_spiders.pipelines.HBaseExportPipeline': 1}
HBASE_ZK='192.168.49.2'
#SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
#SCHEDULER_PERSIST = True
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
#REDIE_URL = None
#REDIS_HOST = '192.168.1.199'
#REDIS_PORT = 6379

DOWNLOAD_DELAY = 0.5  # 间隔时间
#COMMANDS_MODULE = 'Sina_spider2.commands'
# LOG_LEVEL = 'INFO'  # 日志级别
# CONCURRENT_REQUESTS = 1
# CONCURRENT_ITEMS = 1
# CONCURRENT_REQUESTS_PER_IP = 1
