from __future__ import annotations
from ojuzmanager.OjuzManager import OjuzManager
import aiohttp_jinja2
from server import debug
from aiohttp import web
import logging

logger = logging.getLogger("server.handler")
logger.setLevel(logging.DEBUG if debug else logging.INFO)

class SiteHandler:

    def __init__(self, mongo, contest_managers):
        self._mongo = mongo
        self._contest_managers = contest_managers

    @property
    def mongo(self):
        return self._mongo
    
    @property
    def contest_managers(self):
        return self._contest_managers
    
    async def test_submit_post(self, request):
        form = await request.json()
        logger.debug(form)
        ojuz: OjuzManager = self.contest_managers['ojuz']
        submission_url = await ojuz.submit_solution(form["problem_url"], form["solution_code"])
        logger.debug(submission_url)
        return web.json_response({'submission_url': submission_url})

    @aiohttp_jinja2.template("test_submit.html")
    async def test_submit_get(self, request):
        return {}
    
    
    