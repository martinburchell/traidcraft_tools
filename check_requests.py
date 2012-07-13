#!/usr/bin/python

import os.path
import codecs
import locale
import sys

from connect_settings import *

from connect_website import ConnectWebsite

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

script_dir = os.path.dirname(sys.argv[0])
connect_dir = os.path.join(script_dir, 'connect')

website = ConnectWebsite(CONNECT_DOMAIN, CONNECT_LOGIN, CONNECT_PASSWORD,
                         connect_dir)
website.check_requests()
