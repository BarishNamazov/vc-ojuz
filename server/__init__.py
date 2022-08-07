debug = True

import coloredlogs
coloredlogs.install()

from server.server_config import config
from server.main import main