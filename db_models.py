from datetime import datetime

from google.appengine.ext import db

import models

class Person(db.Model):
    """Person who orders lunch."""
    name = db.StringProperty()

class LunchOrder(db.Model):
    """The lunch order for an individual person for one day."""
    date = db.DateProperty()
    restaurant = db.StringProperty()
    order = db.StringProperty()

    person = db.ReferenceProperty(Person, collection_name='lunch_orders')

class Scraper(db.Model):
    """Data about the current state of scraping."""
    last_scrape = db.DateTimeProperty()
    highest_scraped_id = db.IntegerProperty()
    lunchbox_email = db.StringProperty()
    lunchbox_password = db.StringProperty()

    def scrape(self):
        scraper = models.LunchboxScraper()
        parser = models.LunchboxParser()

        scraper.login(self.lunchbox_email, self.lunchbox_password)
        parser.set_scraper(scraper)

        high_seen_id = 0
        parser.scrape_orders_page()
        for order_id in parser.order_ids():
            if order_id <= self.highest_scraped_id:
                continue
            if high_seen_id < order_id:
                high_seen_id = order_id
            parser.scrape_order_page(order_id)
                        
            for name in parser.names():
                p = Person.all().filter('name =', name).get()
                if not p:
                    print "Unknown person", name
                    continue
                lunch_order = LunchOrder(date = parser.order_date(),
                                         restaurant = parser.restaurant(),
                                         order = '',
                                         person = p)
                lunch_order.put()
        self.last_scrape = datetime.now()
        self.highest_scraped_id = high_seen_id
        self.put()
                
