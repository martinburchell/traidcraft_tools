import cookielib
import urllib2
from lxml.html.soupparser import fromstring

class Website(object):
    debug = False

    def __init__(self, domain, login, password):
        cookie_jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        self.insecure_domain = 'http://' + domain
        self.secure_domain = 'https://' + domain
        self.login = login
        self.password = password

    def send_request_and_return_dom(self, url, post_data=None):
        response = self.opener.open(url, post_data)
        content = response.read()
        response.close()

        return fromstring(content)
