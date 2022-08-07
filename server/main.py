import asyncio
import logging
from ojuzmanager.OjuzManager import OjuzManager
from server import debug, config
from server.utils import init_mongo
from aiohttp import web

logger = logging.getLogger("server.main")
logger.setLevel(logging.DEBUG if debug else logging.INFO)

async def setup_mongo(app, loop):
    mongo = await init_mongo(config['mongo'], loop)

    async def close_mongo(app):
        mongo.client.close()

    app.on_cleanup.append(close_mongo)
    return mongo

async def initialize_app(loop):
    app = web.Application(loop=loop)
    mongo = await setup_mongo(app, loop)
    return app


def main():
    # asyncio.get_event_loop() is deprecated since Python 3.10
    try:
        loop = asyncio.get_running_loop()
    except:
        loop = asyncio.new_event_loop()
    app = loop.run_until_complete(initialize_app(loop))
    web.run_app(app, host=config['host'], port=config['port'], loop=loop)