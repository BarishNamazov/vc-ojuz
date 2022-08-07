# Ojuz Manager package

# Make sure to create accounts.py file with account credentials
# or define ojuz_accounts here
from .accounts import ojuz_accounts

debug = True
import coloredlogs
coloredlogs.install()