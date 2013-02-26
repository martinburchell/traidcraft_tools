#!/usr/bin/python

import os.path
import codecs
import locale
import logging
import sys

from connect_settings import *

from connect_website import ConnectWebsite

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

script_dir = os.path.dirname(sys.argv[0])
connect_dir = os.path.join(script_dir, 'connect')

log_dir = os.path.join(script_dir, 'log')
logger = logging.getLogger('check_requests')
logger.addHandler(logging.FileHandler(os.path.join(log_dir, 'check_requests.log')))

website = ConnectWebsite(CONNECT_DOMAIN, CONNECT_LOGIN, CONNECT_PASSWORD,
                         connect_dir, logger)
website.check_requests()
