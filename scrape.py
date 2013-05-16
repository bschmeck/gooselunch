import cookielib
from datetime import datetime
import re
import urllib
import urllib2

class ParseError(Exception):
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
            raise Exception("Not logged in.")
        
        past_orders_url = lunchbox.fm/orders/past
        req = urllib2.Request(past_orders_url)
        f = self.opener.open(req)
        
        return f.read()

# Set up some regexes:
# Find the URLs of past orders on the past order list page
order_regex = re.compile("/orders/view_past/(?P<order_id>\d+)")
# Find the date of an order on a past order page
date_regex = re.compile("<h3 class.*?>(?P<date_string>.*?) from", re.MULTILINE | re.DOTALL)
# Find the names of those who ordered on a past order page
name_regex = re.compile("<td><strong>(?P<name>[A-Z].*?)</strong> wanted")

# Iterate over orders like:
for m in order_regex.finditer(content):
    url = m.group(0)
    order_id = m.group('order_id')

    # If we've already processed order_id then continue

    # For orders we haven't processed, read in the order via url
    # Store that in order_content

    # Get the order's date via:
    date_match = date_regex.search(order_content)
    if not date_match:
        raise ParseError("Unable to find date string for order %s" % url)
    
    order_date = datetime.strptime(date_match.group('date_string').strip(), "%A, %B %d, %Y")

    # Create order object with order_date and URL

    # Iterate over the names of those who ordered like:
    for name_match in name_regex.finditer(order_content):
        name = name_match.group('name')

        # Check that the person ordered for that day
        # Find the person via the name
        # Create a LunchOrder object from the order object and the person object
