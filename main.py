# Imports
import json
import requests
import datetime
import time
from datetime import date
import plotly.plotly as py
import plotly.graph_objs as graph
from pprint import pprint

REST = '/rest'

# Config
config = {'username' : 'marques.art@gmail.com', 'password' : 'bugT3ster', 'uri' : 'https://landfill.bugzilla.org/bugzilla-5.0-branch'}

# Report
class BugzillaReport:

  def __init__(self, username, password, uri):
    """ 
      Constructor with a username, password and uri of the bugzilla server 
      After the BugzillaReport has been initialized, it will have a dictionary data-structure
      containing lists for all the opened, closed, assigned, and so forth bugs.
      According to called methods, this dictionary is filled 
    """
    self.username = username
    self.password = password 
    self.uri = uri + REST
    self.loggedIn = False
    self.loginInfo = None
    self.bugs = { 'opened' : [], 'closed' : [], 'assigned' : [], 'rejected' : [], 'resolved' : [] }

  def isLoggedIn(self):
    """ Verify if the user is logged in """
    if not self.loggedIn:
      raise RuntimeError('Sorry. You are not logged in.')

  def getTokenParam(self):
    """ Add the token parameter to the request uri """
    return '&token=' +self.loginInfo['token']

  def getIncludedFields(self):
    """ Get the list of fields to be extracted from the bug info """
    return '&include_fields=id,component,classification,creation_time,last_change_time,is_open,priority,severity,status,summary'

  def login(self):
    """ Login into the bugzilla server """
    print '>>> Login in'

    loginUri = self.uri + '/login?login=' + self.username + '&password=' +self.password
    data = requests.get(loginUri)
    self.loginInfo = json.loads(data.text)

    print '>>> Successfully logedin' 
    print self.loginInfo
    self.loggedIn = True

  def getBug(self, id):
    """ Get a bug with a specific ID """
    print '>>> Getting bug: [%s]' %(id)
    self.isLoggedIn()

    bugUri = self.uri + '/bug?id=' + str(id) + self.getTokenParam()
    data = requests.get(bugUri)

    print '>>> Bug [%s] info' %(id)
    bug = json.loads(data.text)
    print json.dumps(bug, indent=4, sort_keys=True)

  def getOpenedBugs(self):
    """ Get all opened bugs in the last month """
    currentDate = datetime.date(date.today().year, date.today().month, 01)
    status = 'CONFIRMED'
    dateParam = currentDate.strftime('%Y-%m-%d')

    print '>>> Getting all [%s] bugs created from [%s]' %(status, dateParam)
    self.isLoggedIn()
    bugUri = self.uri + '/bug?status=' + status + '&last_change_time=' + dateParam + self.getIncludedFields() + self.getTokenParam()
    self.bugs['opened'].extend(self.getBugs(status, dateParam))

  def getClosedBugs(self):
    """ Get all cloed bugs in the last month """
    currentDate = datetime.date(date.today().year, date.today().month, 01)
    status = 'RESOLVED'
    dateParam = currentDate.strftime('%Y-%m-%d')
    print '>>> Getting all [%s] bugs closed from [%s]' %(status, dateParam)
    self.bugs['closed'].extend(self.getBugs(status, dateParam))

  def getBugs(self, status, dateParam):
    """ Get bugs with a specific status in a date range """
    self.isLoggedIn()
    bugUri = self.uri + '/bug?status=' + status + '&last_change_time=' + dateParam + self.getIncludedFields() + self.getTokenParam()
    data = requests.get(bugUri)

    bugList = json.loads(data.text)
    print '>>> %s Bugs retrieved' %(len(bugList['bugs']))
    #print json.dumps(bugList['bugs'], indent=4, sort_keys=True)
    return bugList['bugs']


  def countBugsOfDay(self, day, bugList):
    """ Count the number of bugs on a day """
    return sum(1 for bug in bugList if self.getDateOfBug(bug) == day)

  def getDateOfBug(self, bug):
    """ 
      Get the date of a bug in order to compare it with a dateTime
    """
    # FIXME: I am new to python. There may be a easy way to do this. But I'm still looking into it.
    return datetime.datetime.strptime(json.dumps(bug['last_change_time']), '"%Y-%m-%dT%H:%M:%SZ"').date()

  def viewBugsPerDayOf(self, bugList):
    """ 
      Generate a graph of bugs (axis Y) per day (axis X) of given bug list
    """
    x = [];
    y = [];

    for day in range(0 , (date.today().day)):
      # get the current day of the month
      currentDay = datetime.date(date.today().year, date.today().month, (day + 1))
      x.append(currentDay)

      # get the number of bugs in that day
      numberOfBugsInDay = self.countBugsOfDay(currentDay, bugList)
      y.append(numberOfBugsInDay)

      print 'In %s there were %s bugs' %(currentDay, numberOfBugsInDay)

    return graph.Scatter(x=x, y=y)

  def viewBugsPerDay(self):
    """ Generate a report of opened and closed bugs per day of a give bugzilla server """
    opened = self.viewBugsPerDayOf(self.bugs['opened'])
    closed = self.viewBugsPerDayOf(self.bugs['closed'])

    data = [opened, closed]
    
    return data

  def countBugsOfComponent(self, component, bugList):
    """ Count the number of bugs of a component """
    return sum(1 for bug in bugList if json.dumps(bug['component']).strip('"') == component)

  def countBugsOfComponentWithSeverity(self, component, severity, bugList):
    """ Count the number of bugs of a component with a given severity"""
    return sum(1 for bug in bugList if json.dumps(bug['component']).strip('"') == component and json.dumps(bug['severity']).strip('"') == severity)

  def viewBugsPerComponentOf(self, bugList):
    """ 
      
    """
    
    components = []
    severities = []
    
    data = []

    for bug in bugList:
      bugComponent = json.dumps(bug['component']).strip('"')
      bugSeverity = json.dumps(bug['severity']).strip('"')
      if not bugComponent in components:
        components.append(bugComponent)
      if not bugSeverity in severities:
        severities.append(bugSeverity)
        
    print components
    print severities
    print ''

    count = 0
    for component in components:
      x = []
      y = []
      diameters = []

      numberOfBugsInComponent = self.countBugsOfComponent(component, bugList)
      print '%s %s' %(component, numberOfBugsInComponent)

      for severity in severities:
        numberOfBugsInSeverity = self.countBugsOfComponentWithSeverity(component, severity, bugList)
        print ' %s %s' %(severity, numberOfBugsInSeverity)
        x.append(severity)
        y.append(numberOfBugsInSeverity)

      
      
      trace = graph.Bar(x=x, y=y, name=component)
      data.append(trace)

      count += 1
      if count == 3:
        break


      
    pprint(data)
    return data   




  def viewBugsPerComponent(self):
    """ 
      Generate a report of bugs per component. 
      Currently it only generates the bugs that are opened
    """
    

    
    
    return self.viewBugsPerComponentOf(self.bugs['opened'])



# Some methods for test, at leat while I am developing the tool
report = BugzillaReport(config['username'], config['password'], config['uri'])
report.login()
report.getOpenedBugs()
report.getClosedBugs()
# data=report.viewBugsPerDay()
# plot_url = py.plot(data, filename='number-of-bugs-per-day')
data = report.viewBugsPerComponent()
layout = graph.Layout(barmode='group')

fig = graph.Figure(data=data, layout=layout)
plot_url = py.plot(data, filename='number-of-bugs-per-component-per-severity')