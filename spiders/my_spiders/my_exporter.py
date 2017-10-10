
from scrapy.exporters import BaseItemExporter

class HBaseRowItemExporter(BaseItemExporter):

    def __init__(self, conn, **kwargs):
        self._configure(kwargs, dont_fail=True)
        self.conn = conn
 
    def export_item(self, item):
        table = self.conn.table(item.table_name())
        itemdict = dict(self._get_serialized_fields(item))
        vals = {}
        for key, value in itemdict.iteritems():
            vals['cf:%s' % key] = '%s' % value

        table.put('%s' % item.rowkey(), vals)    