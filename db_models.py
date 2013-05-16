from google.appengine.ext import db

class Person(db.Model):
    """Person who orders lunch."""
    name = db.StringProperty()

class LunchOrder(db.Model):
    """The lunch order for an individual person for one day."""
    date = db.DateProperty()
    restaurant = db.StringProperty()
    order = db.StringProperty()

    person = db.ReferenceProperty(Person, collection_name='lunch_orders')

class ScrapeStats(db.Model):
    """Data about the current state of scraping."""
    last_scrape = db.DateProperty()
    highest_scraped_id = db.IntegerProperty()
