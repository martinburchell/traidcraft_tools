import cookielib
import urllib2
from lxml.html.soupparser import fromstring
from retry import retry

class Website(object):
    debug = False

    def __init__(self, domain, login, password, logger=None):
        cookie_jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        self.insecure_domain = 'http://' + domain
        self.secure_domain = 'https://' + domain
        self.login = login
        self.password = password
        self.logger = logger

    def send_request_and_return_dom(self, url, post_data=None):
        response = self.send_request_with_retry(url, post_data)
        content = response.read()
        response.close()

        return fromstring(content)

    @retry(urllib2.URLError, tries=4, delay=3, backoff=2)
    def send_request_with_retry(self, url, post_data):
        return self.opener.open(url, post_data)
