# -*- coding: utf-8 -*-
from scrapy import signals, Item
from scrapy.exporters import JsonLinesItemExporter
from my_spiders.my_exporter import HBaseRowItemExporter
import my_spiders.items
import happybase

item_types = [cls.__name__ for cls in vars()['Item'].__subclasses__()]

class JsonLinesExportPipeline(object):
    def __init__(self):
        self.exporters = {}
        self.item_types = item_types
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        for it in self.item_types:
            self.init_exporter(it)
        

    def init_exporter(self, item_type):
        self.files[item_type] = open(item_type + ".json", 'a')
        self.exporters[item_type] = JsonLinesItemExporter(self.files[item_type], ensure_ascii=False)
        self.exporters[item_type].start_exporting()

    def spider_closed(self, spider):
        for it in self.item_types:
            self.exporters[it].finish_exporting()
            out_file = self.files.pop(it)
            out_file.close()

    def process_item(self, item, spider):
        self.exporters[item.__class__.__name__].export_item(item)
        return item
        
class HBaseExportPipeline(object):
    
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        self.conn = happybase.Connection(spider.settings.get("HBASE_ZK"))
        self.exporter = HBaseRowItemExporter(self.conn, ensure_ascii=False)

    def spider_closed(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item  