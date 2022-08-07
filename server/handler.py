from __future__ import annotations
from ojuzmanager.OjuzManager import OjuzManager
import aiohttp_jinja2
from aiohttp import web

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
    
    @aiohttp_jinja2.template("test_submit.html")
    async def test_submit_post(self, request):
        form = await request.post()
        ojuz: OjuzManager = self.contest_managers['ojuz']
        submission_url = await ojuz.submit_solution(form["problem_url"], form["solution_code"])
        return {'submission_url': submission_url, 'form': form}

    @aiohttp_jinja2.template("test_submit.html")
    async def test_submit_get(self, request):
        return {'submission_url': None, 'form': None}
    
    
    