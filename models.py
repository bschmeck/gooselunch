import cookielib
from datetime import datetime
import re
import urllib
import urllib2

class ParseError(Exception):
    pass

class ScrapeError(Exception):
    pass

class LunchboxParser:
    def __init__(self):
        # Find the URLs of past orders on the past order list page
        self.order_regex = re.compile("/orders/view_past/(?P<order_id>\d+)")
        # Find the date of an order on a past order page
        self.date_regex = re.compile("<h3 class.*?>(?P<date_string>.*?) from", re.MULTILINE | re.DOTALL)
        # Find the names of those who ordered on a past order page
        self.name_regex = re.compile("<td><strong>(?P<name>[A-Z].*?)</strong> wanted")

    def set_orders_page(self):
        self.orders_page = self.lunchbox.past_orders()
        
    def set_order_page(self, order_id):
        self.order_page = self.lunchbox.past_order(order_id)
        
    def parse(self, email, password):
        self.lunchbox = LunchboxScraper()
        self.lunchbox.login(email, password)

        if not self.lunchbox.logged_in:
            raise ParseError("Invalid email or password.")
        
        self.set_orders_page()
        for order_id in self.order_ids():
            # TODO: If we've already processed order_id then continue
            self.set_order_page(order_id)
            order_date = self.order_date()
            for name in self.names():
                # TODO: Check that the person ordered for that day
                # TODO: Find the person via the name
                # TODO: Create a LunchOrder object from the order object and the person object
                pass
                
    def order_ids(self):
        return map(lambda x: x.group('order_id'), self.order_regex.finditer(self.orders_page))

    def order_date(self):
        date_match = self.date_regex.search(self.order_page)
        if not date_match:
            raise ParseError("Unable to find date string for order %s" % url)
    
        return datetime.strptime(date_match.group('date_string').strip(), "%A, %B %d, %Y")
    
    def names(self):
        return map(lambda x: x.group('name'), self.name_regex.finditer(self.order_page))

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
        
        past_order_url = 'http://lunchbox.fm/orders/view_past/' + order_id
        req = urllib2.Request(past_order_url)
        f = self.opener.open(req)
        
        if f.geturl() != past_order_url:
            raise ScrapeError("Unable to view order " + order_id)

        return f.read()