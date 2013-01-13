import json
import os.path
import urllib
from urllib2 import HTTPError

from lxml.cssselect import CSSSelector

from website import Website

class ShopWebsite(Website):

    def __init__(self, login, password, tracking_directory):
        super(ShopWebsite, self).__init__('www.traidcraftshop.co.uk',
                                         login, password)
        self.signin_page = self.secure_domain + '/signin.aspx'
        self.tracking_directory = tracking_directory

    def track_orders(self, max=2):
        self.log_in()
        order_history_page = self.secure_domain + '/orderhistorytc.aspx'

        root = self.send_request_and_return_dom(order_history_page)
        selector = CSSSelector('#tblOrderHistory td a')

        order_count = 0

        for a in selector(root):
            order_number = a.text.strip()
            order_url = a.get('href')

            if self.debug:
                print 'order:' + order_number
            
            self.track_order(order_number, order_url)

            order_count +=1
            if order_count > max:
                break

    def track_order(self, order_number, order_url):
        root = self.send_request_and_return_dom(self.secure_domain + '/' +
                                                order_url)
        selector = CSSSelector('#tblItemHistory td a')

        consignments = {}

        for a in selector(root):
            if a.text is not None:
                consignments[a.text.strip()] = a.get('href')

        if len(consignments) == 0 and self.debug:
            print 'No consignments yet'

        for consignment_number, consignment_url in consignments.items():
            if self.debug:
                print 'consignment:' + consignment_number
            self.track_activity(order_number,
                                consignment_number, consignment_url)

    def track_activity(self, order_number, consignment_number, tracking_url):

        try:
            new_log = self.get_new_log(tracking_url)
        except HTTPError:
            print 'Unable to load page %s' % tracking_url
            return

        order_directory = os.path.join(self.tracking_directory, order_number)
        file_name = os.path.join(order_directory, consignment_number + '.json')
        old_log = self.get_old_log(file_name)

        if new_log != old_log:
            print 'Changes to log for order %s, consignment %s:' % \
                  (order_number, consignment_number)
            print '*before*:'
            self.dump_log(old_log)
            print '*after*:'
            self.dump_log(new_log)
            print

            if not os.path.exists(order_directory):
                os.makedirs(order_directory)
            with open(file_name, 'w') as file:
                json.dump(new_log, file)

    def dump_log(self, log):
        for entry in log:
            for column in self.get_tracking_columns():
                cell = u'%s\t' % entry[column]
                print cell,
            print


    def get_new_log(self, tracking_url):
        root = self.send_request_and_return_dom(tracking_url)

        selector = CSSSelector('.trackingtable tr td')

        log = []

        i = iter(self.get_tracking_column())
        entry = {}

        for td in selector(root):
            column = i.next()

            if td.text is not None:
                entry[column] = td.text.strip()
            else:
                entry[column] = ''
                
            if column == 'items':
                log.append(entry)
                entry = {}

        return log

    def get_old_log(self, file_name):
        try:
            with open(file_name) as file:
                log = json.load(file)
        except IOError:
            log = []

        return log


    def get_tracking_column(self):
        while True:
            for column in self.get_tracking_columns():
                yield column

    def get_tracking_columns(self):
        return ['date', 'time', 'activity', 'location', 'items']

    def log_in(self):

        fields = self.read_hidden_fields()

        fields['EMail'] = self.login
        fields['txtPassword'] = self.password
        fields['existingLoginButton'] = 'Login'

        login_data = urllib.urlencode(fields)

        if self.debug:
            print 'Logging in...'
        
        response = self.send_request_with_retry(self.signin_page, login_data)
        response.close()
        

    def read_hidden_fields(self):
        root = self.send_request_and_return_dom(self.signin_page)
        selector = CSSSelector('[type=hidden]')

        fields = {}

        for element in selector(root):
            fields[element.get('name')] = element.get('value')

        return fields
        
