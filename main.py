# Imports
from data import Bugzilla
import plotly.plotly as py
import plotly.graph_objs as graph

# Config
config = {'username' : 'marques.art@gmail.com', 'password' : 'bugT3ster', 'uri' : 'https://landfill.bugzilla.org/bugzilla-5.0-branch'}



# Some methods for test, at leat while I am developing the tool
bugzillaData = Bugzilla(config['username'], config['password'], config['uri'])
bugzillaData.setUp()
bugzillaData.extractData(None)

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