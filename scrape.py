import cookielib
import re
import urllib
import urllib2

class ScrapeError(Exception):
    pass

class LunchboxScraper:
    def __init__(self):
        self.jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        self.logged_in = False

    def login(self, email, password):
        login_url = "http://lunchbox.fm"
        f = self.opener.open(login_url)

        login_page = f.read()
        # We need to submit 2 hidden fields along with email and password
        # There are 2 forms on the page, login and forgot password, we need the
        # the key and fields token from the login form, which comes first
        match = re.search('data\[_Token\]\[fields\]" value="(.*?)"', login_page)
        if match:
            fields_token = match.group(1)
        else:
            raise ScrapeError("Unable to find data[_Token][fields]")
        match = re.search('data\[_Token\]\[key\]" value="(.*?)"', login_page)
        if match:
            key_token = match.group(1)
        else:
            raise ScrapeError("Unable to find data[_Token][key]")

        # Grab data[_Token][fields] and data[_Token][key] from the form
        values = {'data[User][email]': email,
                  'data[User][password]': password,
                  'data[User][remember_me]': 0, 
                  'data[_Token][key]': key_token, 
                  'data[_Token][fields]': fields_token}

        data = urllib.urlencode(values)
        req = urllib2.Request(login_url, data)
        f = self.opener.open(req)

        # Check that we were authenticated
        self.logged_in = f.geturl() == 'http://lunchbox.fm/orders'

    def past_orders(self):
        if not self.logged_in:
            raise ScrapeError("Not logged in.")
        
        past_orders_url = 'http://lunchbox.fm/orders/past'
        req = urllib2.Request(past_orders_url)
        f = self.opener.open(req)
        
        return f.read()

    def past_order(self, order_id):
        if not self.logged_in:
            raise ScrapeError("Not logged in.")
        
        past_order_url = 'http://lunchbox.fm/orders/view_past/%d' % order_id
        req = urllib2.Request(past_order_url)
        f = self.opener.open(req)
        
        if f.geturl() != past_order_url:
            raise ScrapeError("Unable to view order %d." % order_id)

        return f.read()
