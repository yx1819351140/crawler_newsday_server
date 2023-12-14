import hashlib
from pymongo import MongoClient
from simhash import Simhash
import redis
from crawler_newsday_server.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, MONGO_URL, MONGO_TABLE, MONGO_DB, MONGO_DB1


def calculate_simhash(text):
    # 取前一千个字符，不够一千取全文
    truncated_text = text[:1000] if len(text) > 1000 else text
    # 计算 Simhash 值
    simhash_value = Simhash(truncated_text).value
    return simhash_value


def check_duplicate(redis_client, simhash_key, simhash_value):
    # 获取前16位作为key
    key_prefix = simhash_value >> 48
    key = f"{simhash_key}:{key_prefix}"

    # 在 Redis 中获取对应的值
    stored_hashes = redis_client.hget(simhash_key, key)

    if stored_hashes:
        # 如果key存在，解析存储的hash值列表
        stored_hashes = stored_hashes.decode('utf-8').split(',')

        if str(simhash_value) in stored_hashes:
            # 如果Simhash值已经存在于列表中，表示重复
            return True
        else:
            # 如果Simhash值不存在于列表中，添加到列表并返回False
            stored_hashes.append(str(simhash_value))
            redis_client.hset(simhash_key, key, ','.join(stored_hashes))
            return False
    else:
        # 如果key不存在，创建新的hash集合并返回False
        redis_client.hset(simhash_key, key, str(simhash_value))
        return False


def run():
    # 连接 MongoDB
    mongo_client = MongoClient(MONGO_URL)
    db = mongo_client[MONGO_DB]
    db1 = mongo_client[MONGO_DB1]
    collection = db[MONGO_TABLE]
    collection1 = db1[MONGO_TABLE]

    # 连接 Redis
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

    # Simhash key
    simhash_key = 'news_simhash'

    # 从 MongoDB 中读取新闻正文并计算 Simhash 值
    for document in collection.find():
        news_text = document.get('news_content', '')
        if news_text:
            simhash_value = calculate_simhash(news_text)

            # 检查是否重复
            is_duplicate = check_duplicate(redis_client, simhash_key, simhash_value)

            if not is_duplicate:
                collection1.insert_one(document)


if __name__ == '__main__':
    run()
