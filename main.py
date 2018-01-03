# Imports
from data import Bugzilla
import sys
import plotly.plotly as py
import plotly.graph_objs as graph

import datetime
import time
from time import mktime
from datetime import date

# Config
config = {'username' : 'marques.art@gmail.com', 'password' : 'bugT3ster', 'uri' : 'https://landfill.bugzilla.org/bugzilla-5.0-branch'}

FROM_DATE = 1
TO_DATE = 2
DEFAULT_ARGS_LENGTH = 1
DATE_STR_FORMAT = "%Y%m%d"


# Some methods for test, at leat while I am developing the tool
bugzillaData = Bugzilla(config['username'], config['password'], config['uri'])
bugzillaData.setUp()

fromDate = None
toDate = None

try:
	fromDateStr = sys.argv[FROM_DATE]
	fromDate = datetime.datetime.strptime(fromDateStr, DATE_STR_FORMAT).date()
except IndexError:
	fromDate = datetime.date(date.today().year, date.today().month, 01)

try:
	toDateStr = sys.argv[TO_DATE]
	toDate = datetime.datetime.strptime(toDateStr, DATE_STR_FORMAT).date()
except IndexError:
	fromDate = datetime.date(date.today().year, date.today().month, date.today().day)

bugzillaData.extractData(fromDate, toDate)

# result.getOpenedBugs()
# result.getClosedBugs()
# data=report.viewBugsPerDay()
# plot_url = py.plot(data, filename='number-of-bugs-per-day')
#data = report.viewBugsPerComponent()
#layout = graph.Layout(barmode='group')
#fig = graph.Figure(data=data, layout=layout)
#plot_url = py.plot(data, filename='number-of-bugs-per-component-per-severity')

# data = result.viewBugsPerAssignee()
# plot_url = py.plot(data, filename='bugs-per-assignee')
