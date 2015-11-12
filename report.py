import json
import requests
import datetime
import time
from datetime import date
import plotly.plotly as py
import plotly.graph_objs as graph
from pprint import pprint

REST = '/rest'

INCLUDE_FIELDS = '&include_fields=id,component,classification,creation_time,last_change_time,is_open,priority,severity,status,summary,assigned_to,resolution'

BUG_STATUS_FIELD_NAME = 'bug_status'

BUG_RESOLUTION_FIELD_NAME = 'resolution'

class bugzilla:
  """ Bugzilla report API get data from a bugzilla 5.0 server in order to build a bug report"""

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
    self.status = []
    self.resolutions = []
    self.bugs = {'all' : []}
    
  def isLoggedIn(self):
    """ Verify if the user is logged in """
    if not self.loggedIn:
      raise RuntimeError('Sorry. You are not logged in.')

  def getTokenParam(self):
    """ Add the token parameter to the request uri """
    return 'token=' +self.loginInfo['token']

  def setUp(self):
    """ 
      Set up the initial data required in order to create the report 
      Such set up includes logging in and extracting configurable bug statuses and resolutions
    """
    self.login()

    data = self.getField(BUG_STATUS_FIELD_NAME)
    self.setBugStatus(data)

    data = self.getField(BUG_RESOLUTION_FIELD_NAME)
    self.setBugResolutions(data)

  def getField(self, fieldName):
    """ Acquiring information of bugzilla fields """
    self.isLoggedIn()
    bugUri = self.uri + '/field/bug/'+ fieldName + '?' + self.getTokenParam()
    data = requests.get(bugUri)
    fieldInfo = json.loads(data.text)

    return fieldInfo

  def setBugResolutions(self, resolutionList):
    """ Set the bug resoluntions values """
    for resolution in resolutionList['fields'][0]['values']:

      if resolution['name'] is not None:
        name = json.dumps(resolution['name']).strip('"')
        if name : self.resolutions.append(name)

    print '>>> REPOSITORY BUG RESOLUTIONS :: %s' %(self.resolutions)

  def setBugStatus(self, statusList):
    """ Set the bug statuses values """
    for status in statusList['fields'][0]['values']:

      if status['name'] is not None:
        name = json.dumps(status['name']).strip('"')
        self.status.append(name)
        self.bugs.update({name : []})

    print '>>> REPOSITORY STATUSES :: %s' %(self.status)

  def getIncludedFields(self):
    """ Get the list of fields to be extracted from the bug info """
    return INCLUDE_FIELDS

  def login(self):
    """ Login into the bugzilla server """
    print '>>> Login in'

    loginUri = self.uri + '/login?login=' + self.username + '&password=' +self.password
    data = requests.get(loginUri)
    self.loginInfo = json.loads(data.text)

    print '>>> Successfully logedin :: %s' %(json.dumps(self.loginInfo))
    self.loggedIn = True

  def getBug(self, id):
    """ Get a bug with a specific ID """
    print '>>> Getting bug: [%s]' %(id)
    self.isLoggedIn()
    bugUri = self.uri + '/bug?id=' + str(id) + '&'+ self.getTokenParam()
    data = requests.get(bugUri)
    bug = json.loads(data.text)
    print '>>> Bug [%s] info' %(id)
    print json.dumps(bug, indent=4, sort_keys=True)

  def getBugs(self, status, dateParam):
    """ Get bugs with a specific status in a date range """
    print '\n>>> Getting all [%s] bugs created after [%s]' %(status, dateParam)

    self.isLoggedIn()
    bugUri = self.uri + '/bug?status=' + status + '&last_change_time=' + dateParam + self.getIncludedFields() +'&'+ self.getTokenParam()
    data = requests.get(bugUri)
    bugs = json.loads(data.text)

    print '>>>>>> %s Bugs retrieved' %(len(bugs['bugs']))
    return bugs['bugs']

  def countBugsOfDay(self, day, bugs):
    """ Count the number of bugs on a day """
    return sum(1 for bug in bugs if self.getDateOfBug(bug) == day)

  def getDateOfBug(self, bug):
    """ 
      Get the date of a bug in order to compare it with a dateTime
    """
    # FIXME: I am new to python. There may be a easy way to do this. But I'm still looking into it.
    return datetime.datetime.strptime(json.dumps(bug['last_change_time']), '"%Y-%m-%dT%H:%M:%SZ"').date()

  def extractBugsPerDayOf(self, status, bugs):
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
      numberOfBugsInDay = self.countBugsOfDay(currentDay, bugs)
      y.append(numberOfBugsInDay)

      print 'In %s there were %s bugs' %(currentDay, numberOfBugsInDay)

    return graph.Scatter(x=x, y=y, name=status)

  def extractBugsPerDay(self):
    """ Generate a report of opened and closed bugs per day of a give bugzilla server """
    data = []
    for status in self.status:
      result = self.extractBugsPerDayOf(status, self.bugs[status])
      data.append(result)
    
    return data

  def countBugsOfComponent(self, component, bugs):
    """ Count the number of bugs of a component """
    return sum(1 for bug in bugs if json.dumps(bug['component']).strip('"') == component)

  def countBugsOfComponentWithSeverity(self, component, severity, bugs):
    """ Count the number of bugs of a component with a given severity"""
    return sum(1 for bug in bugs if 
        json.dumps(bug['component']).strip('"') == component and 
        json.dumps(bug['severity']).strip('"') == severity
      )

  def viewBugsPerComponentOf(self, bugs):
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

  def viewBugsPerComponent(self):
    """ 
      Generate a report of bugs per component. 
      Currently it only generates the bugs that are opened
    """
    return self.viewBugsPerComponentOf(self.bugs['opened'])

  def viewBugsPerAssigneeOf(self, bugs):
    assignees = []
    data = []
    
    # Building up the bug list per assignee
    for bug in bugs:
      assigned_to = json.dumps(bug['assigned_to']).strip('"')
      bugSeverity = json.dumps(bug['severity']).strip('"')
      bugStatus = json.dumps(bug['status']).strip('"')
      bugResolution = json.dumps(bug['resolution']).strip('"')
      bugId = json.dumps(bug['id']).strip('"')

      if not assigned_to in assignees:
        assignees.append(dict(name = assigned_to, bugs = [],))

      currently_assinged_to = filter(lambda assignee: assignee['name'] == assigned_to, assignees)[0]
      bugs = currently_assinged_to['bugs']
      bugs.append(dict(bug_id=bugId, severity=bugSeverity, resolution=bugResolution, status= bugStatus))

    # Mapping it to a pie-donut chart

    bug_status = ['VERIFIED', 'CONFIRMED', 'RESOLVED']
    bug_resolution = ['FIXED', 'DUPLICATE']

    for assignee in assignees:      
      bugs_confirmed = sum(1 for bug in assignee['bugs'] if bug['status'] == 'CONFIRMED')
      bugs_resolved = sum(1 for bug in assignee['bugs'] if bug['status'] == 'RESOLVED')
      bugs_verified = sum(1 for bug in assignee['bugs'] if bug['status'] == 'VERIFIED')

      bugs_fixed = sum(1 for bug in assignee['bugs'] if bug['resolution'] == 'FIXED')
      bugs_dublicated = sum(1 for bug in assignee['bugs'] if bug['resolution'] == 'DUPLICATE')

      if not bugs_confirmed == 0 or not bugs_resolved == 0 or not bugs_verified == 0:
        trace = graph.Bar(
          x=bug_status, 
          y=[bugs_verified, bugs_confirmed, bugs_resolved], 
          name=assignee['name'][0 : assignee['name'].index('@')])
        data.append(trace)

    return data

  def viewBugsPerAssignee(self):
    """ 
      Generate a report of bugs per component. 
      Currently it only generates the bugs that are opened
    """
    return self.viewBugsPerAssigneeOf(self.bugs['all'])

  def extractData(self, params):
    """ Extracts from the bugzilla server the necessary data in oder to build a meaningful bug report """

    print params
    currentDate = datetime.date(date.today().year, date.today().month, 01)
    dateParam = currentDate.strftime('%Y-%m-%d')

    for status in self.status:
      bugs = self.getBugs(status, dateParam)
      self.bugs[status].extend(bugs)
      self.bugs['all'].extend(bugs)
    