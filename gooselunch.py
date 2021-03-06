from collections import defaultdict
from datetime import datetime, timedelta
import jinja2
import os
import webapp2

from db_models import LunchOrder, Person, Scraper

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def dates_from_request(request):
        start = request.get("start")
        if start:
            start = datetime.strptime(start, "%Y%m%d").date()
        end = request.get("end")
        if end:
            end = datetime.strptime(end, "%Y%m%d").date()
        
        return (start, end)

class Cron(webapp2.RequestHandler):
    def get(self, job):
        if job == "scrape":
            self.scrape()
        else:
            self.error(400)
    
    def scrape(self):
        scraper = Scraper.all().get()
        scraper.scrape()
    
class OrderSummary(webapp2.RequestHandler):
    def get(self):
        start, end = dates_from_request(self.request)
        if start and end and start > end:
            self.abort(400)
    
        query = LunchOrder.all()
        if start:
            query.filter("date >= ", start)
        if end:
            query.filter("date <= ", end)
        
        totals = defaultdict(int)
        for lunch_order in query.run():
            totals[(lunch_order.person.name, lunch_order.person.key().name())] += 1
            
        template_values = {'totals': totals, 'updated_at': Scraper.all().get().last_scrape}
        if start:
            template_values['start_str'] = start.strftime("%m/%d/%Y")
            template_values['start'] = start.strftime("%Y%m%d")
        else:
            template_values['start_str'] = "the beginning of time"
        if end:
            template_values['end_str'] = end.strftime("%m/%d/%Y")
            template_values['end'] = end.strftime("%Y%m%d")
        else:
            template_values['end_str'] = "the end of time"

        template = JINJA_ENVIRONMENT.get_template('order_summary.html')
        self.response.write(template.render(template_values))
        
class Index(webapp2.RequestHandler):
    def get(self):
        template_values = {'people': Person.all().run()}
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class AddPerson(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name")
        key = self.request.get("key")
        Person(key_name=key, name=name).put()
        
class PersonSummary(webapp2.RequestHandler):
    def get(self, name):
        start, end = dates_from_request(self.request)
        if start and end and start > end:
            self.abort(400)
            
        person = Person.get_by_key_name(name)
        if not person:
            self.abort(404)

        query = person.lunch_orders
        if start:
            query.filter("date >= ", start)
        if end:
            query.filter("date <= ", end)
        query.order("date")

        template_values = {'count': query.count(),
                           'query': query,
                           'person': person,
                           'updated_at': Scraper.all().get().last_scrape}
        if start:
            template_values['start_str'] = start.strftime("%m/%d/%Y")
        else:
            template_values['start_str'] = "the beginning of time"
        if end:
            template_values['end_str'] = end.strftime("%m/%d/%Y")
        else:
            template_values['end_str'] = "the end of time"

        template = JINJA_ENVIRONMENT.get_template('person_summary.html')
        self.response.write(template.render(template_values))
        
app = webapp2.WSGIApplication([('^/?$', Index),
                               ('^/orders/?$', OrderSummary),
                               ('/cron/(.*)/?$', Cron),
                               ('^/orders/(.+?)/?$', PersonSummary),
                               ('^/add_person/?$', AddPerson),],
                              debug=True)

