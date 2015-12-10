import json
import plotly.plotly as py
import plotly.graph_objs as graph
from pprint import pprint


class Component:

  def __init__(self, status, resolutions, bugs):
    self.status = status
    self.resolutions = resolutions
    self.bugs = bugs


  def countBugsOfComponent(self, component, bugs):
    """ Count the number of bugs of a component """
    return sum(1 for bug in bugs if json.dumps(bug['component']).strip('"') == component)

  def countBugsOfComponentWithSeverity(self, component, severity, bugs):
    """ Count the number of bugs of a component with a given severity"""
    return sum(1 for bug in bugs if 
        json.dumps(bug['component']).strip('"') == component and 
        json.dumps(bug['severity']).strip('"') == severity
      )

  def extractBugsPerComponentOf(self, bugs):
    components = []
    severities = []
    data = []

    for bug in bugs:
      bugComponent = json.dumps(bug['component']).strip('"')
      bugSeverity = json.dumps(bug['severity']).strip('"')
      if not bugComponent in components:
        components.append(bugComponent)
      if not bugSeverity in severities:
        severities.append(bugSeverity)

    count = 0
    for component in components:
      x = []
      y = []
      diameters = []

      numberOfBugsInComponent = self.countBugsOfComponent(component, bugs)
      print '%s %s' %(component, numberOfBugsInComponent)

      for severity in severities:
        numberOfBugsInSeverity = self.countBugsOfComponentWithSeverity(component, severity, bugs)
        print ' %s %s' %(severity, numberOfBugsInSeverity)
        x.append(severity)
        y.append(numberOfBugsInSeverity)
      
      trace = graph.Bar(x=x, y=y, name=component)
      data.append(trace)

    return data   

  def extractBugsPerComponent(self):
    """ 
      Generate a report of bugs per component. 
      Currently it only generates the report for all the bugs
      Later on, params will define which statuses will be used
    """
    print '\nGenerating classification of bugs per component grouped by severity\n'
    data = self.extractBugsPerComponentOf(self.bugs['all'])

    return data