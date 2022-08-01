"""
This server similar/same purposes as OjuzSession.py but requests are synchronously made.
Not used but keeping here in case anybody wants to take a look.
If you want to run this file, run: `pip install requests`.
"""
from requests import Session
from bs4 import BeautifulSoup

class OjuzSession:
    """An abstraction for submitting oj.uz solutions given user credentials"""

    csrf_token_name = 'csrf_token'
    generic_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
        'Connection': 'keep-alive',
        'DNT': '1'
    }
    login_url = "https://oj.uz/login?next=/?"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = Session()
        self.logged_in = False
        self.session.get(OjuzSession.login_url)
    
    def get_csfr_token(self, url):
        """Returns the csfr token from given url
        
        url (string): the url that should contain a form/csfr token

        return (string): the csfr token to add to the payload

        """
        req = self.session.get(url, headers = OjuzSession.generic_headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        return soup.find('input', attrs={'name': OjuzSession.csrf_token_name})['value']

    def login(self):
        """Tries to login to oj.uz using given credentials
        Note that even if the session was logged in previously, this will override it.

        return (bool): if the login succeeded

        """
        login_data = {
            'next': ["/?", "/?"],
            'email': self.username,
            'password': self.password,
            'submit': 'Sign+in',
            OjuzSession.csrf_token_name: self.get_csfr_token(OjuzSession.login_url)
        }
        login_headers = OjuzSession.generic_headers | {
            'Referer': OjuzSession.login_url # referer for login is itself
        }
        req = self.session.post(OjuzSession.login_url, data=login_data, headers=login_headers)
        self.logged_in = b'Sign out' in req.content            
        return self.logged_in
    
    def attempt_multiple_logins(self, attempts):
        """Attempts multiple logins until login is successful or attemps are finished
        
        attempts (int): the maximum number of attempts to login

        return (bool): if the login succeeded

        """
        while attempts > 0 and not self.login():
            attempts -= 1
        return self.logged_in

    def submit_solution(self, problem_url, raw_code, attempt_login=True):
        """Submits given code into given problem
        
        problem_url (string): url to the problem itself (not the submission page)
        raw_code (string): code contents

        return (string): the url that contains submission information
        
        """
        if not self.logged_in and attempt_login and not self.login():
            return None
        submit_url = problem_url.replace("problem/view", "problem/submit") # just "view"->"submit" is ambigious
        submit_data = {
            'codes': ["", ""], # not sure why oj.uz wants this
            'language': "9", # C++17, hardcoded for now
            'code_1': raw_code,
            OjuzSession.csrf_token_name: self.get_csfr_token(submit_url),
        }
        submit_headers = OjuzSession.generic_headers | {
            'Referer': submit_url
        }
        req = self.session.post(submit_url, data=submit_data, headers=submit_headers)
        return req.url
    
    def get_content(self, url):
        """Gets HTML content of given url based on this session
        
        return (string): html content of url
        
        """
        req = self.session.get(url)
        return req.content