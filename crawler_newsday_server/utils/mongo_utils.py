from pymongo import MongoClient
from collections import Counter

from scrapy.utils.project import get_project_settings


class MongoDB:

    def __init__(self):
        self.settings = get_project_settings()
        self.client = MongoClient(self.settings.get('MONGO_URL'), connect=False)
        self.db = self.client[self.settings.get('MONGO_DB')]

    def insert_data(self, table, data):
        if not data or not table:
            print('****数据为空****')
            return
        if type(data) == dict:
            self.db[table].insert_one(data)
        elif type(data) == list:
            self.db[table].insert_many(data)

    def is_repeat(self, table, _id):
        return self.db[table].count_documents({"_id": _id})

    def delete_repeat(self, table, field):
        reqs = list(self.db[table].find({}, {field: 1}))
        fileds = [k[field] for k in reqs]
        fileds_sort = sorted(Counter(fileds).items(), key=lambda x: x[1], reverse=True)
        del_ids = [x for x in fileds_sort if x[1] > 1]
        for i in del_ids:
            for k in range(i[1] - 1):
                self.db[table].delete_one({field: i[0]})


if __name__ == '__main__':
    pass
