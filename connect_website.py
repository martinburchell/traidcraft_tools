import csv
import json
import os.path
import urllib

from lxml import etree
from lxml.cssselect import CSSSelector

from website import Website

class ConnectWebsite(Website):
    debug = False

    def __init__(self, domain, login, password, requests_directory):
        super(ConnectWebsite, self).__init__(domain, login, password)
        self.requests_directory = requests_directory
        self.requests_file_name = os.path.join(requests_directory,
                                               'requests.json')
        self.stock_page = self.insecure_domain + '/my_stall/on_hand'

    def update_stock(self, csv_file):
        logged_in = self.log_in()

        if logged_in:
            field_lookup = self.get_product_code_field_lookup()
            post_data = self.get_stock_post_data(csv_file, field_lookup)

            if self.debug:
                print 'Updating stock levels...'
            root = self.send_request_and_return_dom(self.stock_page, post_data)
            selector = CSSSelector('div.notice')

            notice_count = 0

            for notice in selector(root):
                print notice.text
                notice_count += 1

            if notice_count == 0:
                print 'No notices found - check stock levels were updated manually'

    def get_stock_post_data(self, csv_file, field_lookup):
        post_data = {'_method' : 'put',
                     'authenticity_token' : self.token}

        missing_stock = []

        with open(csv_file) as file:
            reader = csv.reader(file, delimiter=',', quotechar='"')
            for row in reader:
                product_code = row[1]
                quantity = int(row[4])
                field_name = field_lookup.get(product_code)
                if field_name is None:
                    missing_stock.append(row)
                else:
                    post_data[field_name] = post_data.get(field_name, 0) + \
                                            quantity

        if len(missing_stock) > 0:
            print 'Not found in online stock list'
            for row in missing_stock:
                print row

        return urllib.urlencode(post_data)

    def get_product_code_field_lookup(self):
        if self.debug:
            print 'Building product code lookup table...'
        root = self.send_request_and_return_dom(self.stock_page)
        selector = CSSSelector('form.edit_store tr td')

        lookup = {}

        for cell in selector(root):
            img = cell.find('img')
            if img is not None:
                product_code = img.get('alt')

            input_field = cell.find('input')
            if input_field is not None:
                field_name = input_field.get('name')
                lookup[product_code] = field_name

        return lookup
        
    def check_requests(self):
        logged_in = self.log_in()

        if logged_in:
            new_requests = self.get_new_requests()
            old_requests = self.get_old_requests()

            if new_requests != old_requests:
                print 'Changes to Traidcraft Requests:'
                print '*before*:'
                self.dump_requests(old_requests)
                print '*after*:'
                self.dump_requests(new_requests)

                with open(self.requests_file_name, 'w') as file:
                    json.dump(new_requests, file)

    def dump_requests(self, requests):
        for request in requests:
            for column in self.get_request_columns():
                cell = '%s\t' % request[column]
                print cell,
            print
            
    def log_in(self):
        self.read_token()

        if self.token is not None:
            session_page = self.secure_domain + '/user_session'

            login_data = urllib.urlencode({'authenticity_token' : self.token,
                                           'user_session[login]' : self.login,
                                           'user_session[password]' : self.password,
                                           'user_session[remember_me]' : 0,
                                           'commit' : 'Log in'})
            if self.debug:
                print 'Logging in...'
            self.opener.open(session_page, login_data).close()
            return True
            
        return False
        
    def read_token(self):
        if self.debug:
            print 'Retrieving token...'
        login_page = self.secure_domain + '/login'
        root = self.send_request_and_return_dom(login_page)
        selector = CSSSelector('[name=authenticity_token]')

        for element in selector(root):
            self.token = element.get('value')

        if self.token is None:
            print 'Failed to retrieve token'

    def get_new_requests(self):
        if self.debug:
            print 'Getting new requests...'
        requests_page = self.insecure_domain + '/my_stall/requests'

        root = self.send_request_and_return_dom(requests_page)
        selector = CSSSelector('#content form tr td')

        requests = []

        i = iter(self.get_request_column())
        request = {}

        for cell in selector(root):
            column = i.next()

            text = cell.text

            if text.strip() == 'Total value:':
                pass

            if column == 'user':
                span = cell.find('span')
                if span is not None:
                    a = span.find('a')
                    text = a.text
            elif column == 'product name':
                a = cell.find('a')
                text = a.text
            
            request[column] = text.strip()           

            if column == 'total price':
                requests.append(request)
                request = {}

        return requests
    
    def get_request_column(self):
        while True:
            for column in self.get_request_columns():
                yield column

    def get_request_columns(self):
        return ['user', 'last update', 'category name', 'product name',
                'quantity', 'unit price', 'total price']

    def get_old_requests(self):
        try:
            with open(self.requests_file_name) as file:
                requests = json.load(file)
        except IOError:
            requests = []

        return requests


        
