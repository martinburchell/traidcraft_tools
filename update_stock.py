#!/usr/bin/python

import os.path
import sys

from connect_settings import *

from connect_website import ConnectWebsite

script_dir = os.path.dirname(sys.argv[0])
connect_dir = os.path.join(script_dir, 'connect')
csv_dir = os.path.join(script_dir, 'csv')

website = ConnectWebsite(CONNECT_DOMAIN, CONNECT_LOGIN, CONNECT_PASSWORD,
                         connect_dir)

csv_file = os.path.join(csv_dir, 'data.csv')
website.update_stock(csv_file)
