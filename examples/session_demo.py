from ojuzmanager import ojuz_accounts
from ojuzmanager.OjuzSession import OjuzSession
import asyncio

username, password = ojuz_accounts[0]

async def main():
    # even though test_submission.cpp is in the same directory as this file
    # this file is supposed to be run from the project root directory.
    # python module structure... sigh..
    with open("examples/test_submission.cpp", "r", encoding='utf-8') as f:
        code = f.read()

    ojuz = OjuzSession(username, password)
    await ojuz.start_session()
    print(await ojuz.login()) # True if login succeeded

    submission_url = await ojuz.submit_solution("https://oj.uz/problem/view/IOI18_combo", code)
    submission_id = str(submission_url).split('/')[-1]

    # prints what's going on for 10 seconds
    for i in range(10):
        print(await ojuz.get_submission_summary(submission_id))
        await asyncio.sleep(2.5)

    await ojuz.close_session()

asyncio.run(main())