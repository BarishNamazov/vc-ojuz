from __future__ import annotations
from ojuzmanager import accounts
from ojuzmanager.OjuzSession import OjuzSession
import asyncio

class OjuzManagerException(Exception):
    pass

class OjuzManager:
    """
    Main manager to interact with oj.uz
    Uses all specified accounts, ignores failed logins.
    Uses LRU to submit.
    """

    def __init__(self) -> None:
        self.logged_sessions: list[OjuzSession] = []
        self.username_to_session: dict[str, OjuzSession] = {}
        self.solution_number: int = 0 # used for indexing
    
    async def initialize_accounts(self) -> None:
        login_tasks = []
        for username, password in accounts:
            ojuz_session = OjuzSession(username, password)
            self.username_to_session[username] = ojuz_session

            await ojuz_session.start_session()
            # we will attempt 3 times to login
            login_tasks.append(asyncio.create_task(ojuz_session.attempt_multiple_logins(3)))

        await asyncio.gather(*login_tasks)
        logged_usernames = []
        for username, password in accounts:
            ojuz_session = self.username_to_session[username]
            if ojuz_session.logged_in:
                self.logged_sessions.append(ojuz_session)
                logged_usernames.append(username)

        if not self.logged_sessions:
            raise OjuzManagerException("Could not login with any of the specified accounts!")
    
        print("The following usernames logged in and are ready to use", logged_usernames)

    async def close_sessions(self):
        await asyncio.gather(*[session.close_session() for session in self.logged_sessions])
        self.username_to_session = {}
        self.solution_number = 0
    
    async def submit_solution(self, problem_url, raw_code):
        active_sessions = len(self.logged_sessions)
        lru_session = self.logged_sessions[self.solution_number % active_sessions]
        self.solution_number += 1 # concurrency-safe to write this before following line
        return await lru_session.submit_solution(problem_url, raw_code)
    
    async def get_submission_summary(self, submission_id):
        return await self.logged_sessions[0].get_submission_summary(submission_id)

    async def get_submission_details_table(self, submission_id):
        return await self.logged_sessions[0].get_submission_details_table(submission_id)