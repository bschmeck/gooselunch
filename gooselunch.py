from collections import defaultdict
from datetime import datetime, timedelta
import jinja2
import os
import webapp2

from db_models import LunchOrder
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def daterange(arr):
        # We are either called with a single date, e.g. 20130401, or a date range 20130401...20130407
        # The way our URL regex works, this shows up as two elements in a list:
        # ["20130401", None] for single dates and ["20130401", "...20130407"] for the range
        # We strip the None (if present) from the list, then join to create a single string
        # Then split on "..." to get a 1 or 2 elt list, and map that to create start and end dates
        daterange = "".join(filter(None, arr))
        dates = map(lambda s: datetime.strptime(s, "%Y%m%d").date(), daterange.split("..."))
        start = dates[0]
        end = dates[1] if len(dates) == 2 else start
        
        return (start, end)

class OrderSummary(webapp2.RequestHandler):
    def get(self):
        start = self.request.get("start")
        if start:
            start = datetime.strptime(start, "%Y%m%d").date()
        end = self.request.get("end")
        if end:
            end = datetime.strptime(end, "%Y%m%d").date()
        
        query = LunchOrder.all()
        if start:
            query.filter("date >= ", start)
        if end:
            query.filter("date <= ", end)
        
        totals = defaultdict(int)
        for lunch_order in query.run():
            total[lunch_order.person.name] += 1
            
        template_values = {'totals': totals}
        if start:
            template_values['start_str'] = start.strftime("%m/%d/%Y")
        else:
            template_values['start_str'] = "the beginning of time"
        if end:
            template_values['end_str'] = end.strftime("%m/%d/%Y")
        else:
            template_values['end_str'] = "the end of time"

        template = JINJA_ENVIRONMENT.get_template('order_summary.html')
        self.response.write(template.render(template_values))
        
app = webapp2.WSGIApplication([('^/orders/?$', OrderSummary)],
                              debug=True)

