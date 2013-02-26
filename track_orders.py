#!/usr/bin/python

import logging
import os
import sys


from shop_settings import *

from shop_website import ShopWebsite

script_dir = os.path.dirname(sys.argv[0])
tracking_dir = os.path.join(script_dir, 'tracking')

log_dir = os.path.join(script_dir, 'log')
logger = logging.getLogger('track_orders')
logger.addHandler(logging.FileHandler(os.path.join(log_dir, 'track_orders.log')))

website = ShopWebsite(SHOP_LOGIN, SHOP_PASSWORD, tracking_dir, logger)
website.track_orders()
