from datetime import datetime
import re

from scrape import LunchboxScraper

class ParseError(Exception):
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
