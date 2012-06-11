#!/usr/bin/python

import sys
import os

from shop_settings import *

from shop_website import ShopWebsite

script_dir = os.path.dirname(sys.argv[0])
tracking_dir = os.path.join(script_dir, 'tracking')

website = ShopWebsite(SHOP_LOGIN, SHOP_PASSWORD, tracking_dir)
website.track_orders()
