from pymongo import MongoClient


MONGO_URL = 'mongodb://crawler_admin:Z3YqnP*vWqwmJt@52.221.188.240:27017/?authSource=admin'
MONGO_DB = 'newsday_crawler_raw'
MONGO_DB1 = ''
MONGO_TABLE = 'newsday_news'
MONGO_TABLE1 = 'newsday_category'

# 连接 MongoDB
mongo_client = MongoClient(MONGO_URL)
db = mongo_client[MONGO_DB]


def get_category(news_source):
    collection = db[MONGO_TABLE]

    data = collection.aggregate(
        [
            {
                "$match": {
                    "news_source": news_source
                }
            },
            {
                "$group": {
                    "_id": "$news_category"
                }
            }
        ]
    )
    return [i['_id'] for i in data]


def run():
    collection = db[MONGO_TABLE1]
    source_list = ['abs_cbn']
    for source_name in source_list:
        data = {'news_source': source_name, 'catrgory_list': get_category(source_name)}
        collection.insert_one(data)
        print(f'{source_name} category insert success!')


if __name__ == '__main__':
    run()
