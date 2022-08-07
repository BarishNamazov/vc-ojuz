import asyncio
import logging
from ojuzmanager.OjuzManager import OjuzManager
from server import debug, config
from server.utils import init_mongo
from server.handler import SiteHandler
from server.setup_routes import setup_routes
from aiohttp import web
import aiohttp_jinja2, jinja2
import pathlib


PROJ_ROOT = pathlib.Path(__file__).parent.parent
TEMPLATES_ROOT = pathlib.Path(__file__).parent / 'templates'

logger = logging.getLogger("server.main")
logger.setLevel(logging.DEBUG if debug else logging.INFO)

async def setup_mongo(app, loop):
    mongo = await init_mongo(config['mongo'], loop)
    app.on_cleanup.append(lambda app: mongo.client.close())
    return mongo

def setup_jinja(app):
    jinja_env = aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(str(TEMPLATES_ROOT)))

async def initialize_vcs(app):
    contest_managers = {}
    ojuz = contest_managers['ojuz'] = OjuzManager()
    await ojuz.initialize_accounts()
    app.on_cleanup.append(lambda app: ojuz.close_sessions())

    return contest_managers

async def initialize_app(loop):
    app = web.Application(loop=loop)
    mongo = await setup_mongo(app, loop)
    contest_managers = await initialize_vcs(app)
    handler = SiteHandler(mongo, contest_managers)
    setup_jinja(app)
    setup_routes(app, handler, PROJ_ROOT)
    return app


def main():
    # asyncio.get_event_loop() is deprecated since Python 3.10
    try:
        loop = asyncio.get_running_loop()
    except:
        loop = asyncio.new_event_loop()
    app = loop.run_until_complete(initialize_app(loop))
    web.run_app(app, host=config['host'], port=config['port'], loop=loop)