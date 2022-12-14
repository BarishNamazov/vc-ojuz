import aiohttp
import asyncio
import logging
from bs4 import BeautifulSoup
from ojuzmanager import debug

logger = logging.getLogger("ojuzmanager.ojuzsession")
logger.setLevel(logging.DEBUG if debug else logging.INFO)

class OjuzSession:
    """An abstraction for submitting oj.uz solutions given user credentials.
    Async implementation, make sure to await when needed.
    """

    csrf_token_name = 'csrf_token'
    generic_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
        'Connection': 'keep-alive',
        'DNT': '1'
    }

    def __init__(self, username, password):
        self.username = username
        self.password = password        
        self.logged_in = False
    
    async def start_session(self):
        self.session = aiohttp.ClientSession()
        logger.info(f"Ojuz session started: {self.session}")
    
    async def close_session(self):
        logger.info(f"Ojuz session closed: {self.session}")
        await self.session.close()

    async def get_csfr_token(self, url):
        """Returns the csfr token from given url
        
        url (string): the url that should contain a form/csfr token

        return (string): the csfr token to add to the payload
        """

        soup = BeautifulSoup(await self.get_html(url), 'html.parser')
        return soup.find('input', attrs={'name': OjuzSession.csrf_token_name})['value']

    async def login(self):
        """Tries to login to oj.uz using given credentials
        Note that even if the session was logged in previously, this will override it.

        return (bool): if the login succeeded
        """

        login_url = "https://oj.uz/login?next=/?"
        login_data = {
            'next': ["/?", "/?"],
            'email': self.username,
            'password': self.password,
            'submit': 'Sign+in',
            OjuzSession.csrf_token_name: await self.get_csfr_token(login_url) # will create self.session if needed
        }
        login_headers = OjuzSession.generic_headers | {
            'Referer': login_url # referer for login is itself
        }
        req = await self.session.post(login_url, data=login_data, headers=login_headers)
        self.logged_in = 'Sign out' in await req.text()
        logger.info(f"Ojuz session logging in attempt: {self.session} login={self.logged_in}")
        return self.logged_in
    
    async def attempt_multiple_logins(self, attempts):
        """Attempts multiple logins until login is successful or attemps are finished
        
        attempts (int): the maximum number of attempts to login

        return (bool): if the login succeeded
        """

        while attempts > 0 and not await self.login():
            attempts -= 1
        return self.logged_in

    async def submit_solution(self, problem_url, raw_code, attempt_login=True):
        """Submits given code into given problem
        
        problem_url (string): url to the problem itself (not the submission page)
        raw_code (string): code contents

        return (URL): the url that contains submission information
        """

        if not self.logged_in and attempt_login and not await self.login():
            return None
        submit_url = problem_url.replace("problem/view", "problem/submit") # just "view"->"submit" is ambigious
        submit_data = {
            'codes': ["", ""], # not sure what this serves for
            'language': "9", # C++17, hardcoded for now
            'code_1': raw_code,
            OjuzSession.csrf_token_name: await self.get_csfr_token(submit_url), # will create self.session if needed
        }
        submit_headers = OjuzSession.generic_headers | {
            'Referer': submit_url
        }
        req = await self.session.post(submit_url, data=submit_data, headers=submit_headers)
        submission_url = str(req.url)

        if submission_url.startswith("https://oj.uz/login"): # log in issue, maybe session timed out?
            self.logged_in = False
            if attempt_login:
                return await self.submit_solution(problem_url, raw_code, attempt_login)
            else:
                return None
        
        # TODO FIX this! this is a bad workaround!
        if submission_url.startswith("https://oj.uz/problem/submit"): # oj.uz blocked the submission!
            logger.warn("oj.uz blocked the submission!")
            await asyncio.sleep(10) # wait 10 seconds
            return await self.submit_solution(problem_url, raw_code, attempt_login) 

        logger.info(f"Ojuz session {self.session} submitted solution URL={req.url}")
        return submission_url


    async def get_submission_summary(self, submission_id):
        """Gets submission summary given submission_id
        
        submission_id (string): id of the submission

        return (dict): a dictionary containing the keys 'compilation_message',
        'evaluating_subtask_order', 'full_score', 'max_execution_time', 'max_memory',
        'score', 'text'.
        """

        if not self.session or self.session.closed:
            await self.start_session()
        
        summary_url = "https://oj.uz/submission/summary/1"
        # this endpoint requires a CSRF token, so we get a random one
        summary_data = {
            'submission_id': submission_id,
            OjuzSession.csrf_token_name: await self.get_csfr_token("https://oj.uz/problem/submit/APIO13_interference"),
        }
        summary_header = OjuzSession.generic_headers | {
            'Referer': f'https://oj.uz/submission/{submission_id}'
        }
        
        req = await self.session.post(summary_url, data=summary_data, headers=summary_header)
        return await req.json()
    
    async def get_submission_details_table(self, submission_id):
        submission_url = f'https://oj.uz/submission/{submission_id}'
        soup = BeautifulSoup(await self.get_html(submission_url), 'html.parser')
        return str(soup.find(id="submission_details"))

    async def get_html(self, url):
        """GETs HTML content of given url with the current session
        
        url (string): url to get

        return (string): html content of url
        """

        if not self.session or self.session.closed:
            await self.start_session()
        req = await self.session.get(url)
        return await req.text()