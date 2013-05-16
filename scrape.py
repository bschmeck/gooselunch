import cookielib
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

        # Grab data[_Token][fields] and data[_Token][key] from the form
        values = {'data[User][email]': 'ben@aisle50.com', 
                  'data[User][password]': 'XXXXX', 
                  'data[User][remember_me]': 0, 
                  'data[_Token][key]': 'KEY', 
                  'data[_Token][fields]': 'FIELDS'}

        data = urllib.urlencode(values)
        req = urllib2.Request(login_url, data)
        f = self.opener.open(req)

        # Check that we were authenticated
        self.logged_in = f.geturl() == 'http://lunchbox.fm/orders'

    def past_orders(self):
        if not self.logged_in:
            raise ScrapeError("Not logged in.")
        
        past_orders_url = lunchbox.fm/orders/past
        req = urllib2.Request(past_orders_url)
        f = self.opener.open(req)
        
        return f.read()
