# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


# class TripadvPipeline:
#     def process_item(self, item, spider):
#         return item


from scrapy.exporters import CsvItemExporter

# MUST CHANGE TO THIS CLASS IN SETTINGS ITEM_PIPELINES
class WriteItemPipeline(object):

    def __init__(self):
        self.filename = 'tripadvisor.csv'

    def open_spider(self, spider):
        self.csvfile = open(self.filename, 'wb') #, newline = '')
        self.exporter = CsvItemExporter(self.csvfile)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.csvfile.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# class PerYearXmlExportPipeline:
#     """Distribute items across multiple XML files according to their 'year' field"""

#     def open_spider(self, spider):
#         self.year_to_exporter = {}

#     def close_spider(self, spider):
#         for exporter in self.year_to_exporter.values():
#             exporter.finish_exporting()

#     def _exporter_for_item(self, item):
#         adapter = ItemAdapter(item)
#         year = adapter['year']
#         if year not in self.year_to_exporter:
#             f = open(f'{year}.xml', 'wb')
#             exporter = XmlItemExporter(f)
#             exporter.start_exporting()
#             self.year_to_exporter[year] = exporter
#         return self.year_to_exporter[year]

#     def process_item(self, item, spider):
#         exporter = self._exporter_for_item(item)
#         exporter.export_item(item)
#         return item

# # exports items from each start_url to a separate CSV
# class PerUrlCsvExportPipeline:

#     def open_spider(self, spider):
#         self.url_to_exporter = {}

#     def close_spider(self, spider):
#         for exporter in self.url_to_exporter.values():
#             exporter.finish_exporting()

#     def _exporter_for_item(self, item):
#         adapter = ItemAdapter(item)
#         url = adapter['url']
#         if url not in self.url_to_exporter:
#             f = open('{}.csv'.format(url), 'wb')
#             exporter = CsvItemExporter(f)
#             exporter.start_exporting()
#             self.url_to_exporter[url] = exporter
#         return self.url_to_exporter[url]

#     def process_item(self, item, spider):
#         exporter = self._exporter_for_item(item)
#         exporter.export_item(item)
#         return item