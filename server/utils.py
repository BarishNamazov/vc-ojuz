import motor.motor_asyncio as aiomotor
import asyncio

class ServerException(Exception):
    pass

async def init_mongo(mongo_config, loop):
    if not mongo_config['host'] or not mongo_config['port']:
        raise ServerException("Mongo configuration host or port is missing! Check server/config.py file.")

    mongo_uri = "mongodb://{}:{}".format(mongo_config['host'], mongo_config['port'])
    conn = aiomotor.AsyncIOMotorClient(
        mongo_uri,
        maxPoolSize=mongo_config['max_pool_size'],
        io_loop=loop
    )
    db_name = mongo_config['database']
    return conn[db_name]
