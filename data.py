import json
import requests
import datetime
import time
import plotly.plotly as py
import plotly.graph_objs as graph

from time import mktime
from datetime import date
from pprint import pprint
from bug_backlog import Backlog
from bug_components import Component
from bug_developers import Assignee

REST = '/rest'

INCLUDE_FIELDS = '&include_fields=id,component,classification,creation_time,last_change_time,is_open,priority,severity,status,summary,assigned_to,resolution'

BUG_STATUS_FIELD_NAME = 'bug_status'

BUG_RESOLUTION_FIELD_NAME = 'resolution'

BACKLOG_CALLBACK = 'backlog_callback'

ASSIGNEES_CALLBACK = 'assignee_callback'

COMPONENTS_CALLBACK = 'component_callback'

STATUS_CALLBACK = 'status_callback'

RESOLUTION_CALLBACK = 'resolutions_callback'

class DataJSONEncoder(json.JSONEncoder):

  def default(self, obj):
    if isinstance(obj, datetime.datetime):
      return obj.isoformat()
    elif isinstance(obj, datetime.date):
      return obj.isoformat()
    elif isinstance(obj, datetime.timedelta):
      return (datetime.datetime.min + obj).time().isoformat()
    elif isinstance(obj, set):
        return list(obj)

    return json.JSONEncoder.default(self, obj)

class Bugzilla:
  """ 
    Bugzilla data extract API.
    Get data from a bugzilla 5.0 server through its REST API
  """

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

  def writeOutput(self, filePath, jsonData, callback):
    """ Write a json callback function to some file output path """
    with open(filePath, 'w') as outfile:
      jsonDump = json.dumps(jsonData, cls=DataJSONEncoder, indent=4, sort_keys=True)
      callback = callback + '(' + jsonDump + ');'
      outfile.write(callback)

      print '>>> output at  %s ' %(filePath)

  def extractData(self, params):
    """ Extracts from the bugzilla server the necessary data in oder to build a meaningful bug report """

    print params
    currentDate = datetime.date(date.today().year, date.today().month, 01)
    dateParam = currentDate.strftime('%Y-%m-%d')

    for status in self.status:
      bugs = self.getBugs(status, dateParam)
      self.bugs[status].extend(bugs)
      self.bugs['all'].extend(bugs)
      

    backlog = Backlog(self.status, self.resolutions, self.bugs)
    backlogData = backlog.extractBugsPerDay()
    
    components = Component(self.status, self.resolutions, self.bugs)
    componentsData = components.extractBugsPerComponent()

    assignees = Assignee(self.status, self.resolutions, self.bugs)
    assigneesData = assignees.extractBugsPerAssignee()

    self.writeOutput('out/backlog.json', backlogData, BACKLOG_CALLBACK)
    self.writeOutput('out/components.json', componentsData, COMPONENTS_CALLBACK)
    self.writeOutput('out/assignees.json', assigneesData, ASSIGNEES_CALLBACK)
    self.writeOutput('out/status.json', self.status, STATUS_CALLBACK)
    self.writeOutput('out/resolutions.json', self.resolutions, RESOLUTION_CALLBACK)

