import json
import plotly.plotly as py
import plotly.graph_objs as graph
from pprint import pprint

class Assignee:

  def __init__(self, status, resolutions, bugs):
    self.status = status
    self.resolutions = resolutions
    self.bugs = bugs  

  def extractBugsPerAssigneeOf(self, bugs):
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
        total = bugs_confirmed + bugs_resolved + bugs_verified
        print '%s %s' %(assignee['name'][0 : assignee['name'].index('@')], total)
        print ' %s %s' %('verified', bugs_verified)
        print ' %s %s' %('confirmed', bugs_confirmed)
        print ' %s %s' %('resolved', bugs_resolved)
        
        trace = graph.Bar(
          x=bug_status, 
          y=[bugs_verified, bugs_confirmed, bugs_resolved], 
          name=assignee['name'][0 : assignee['name'].index('@')])
        data.append(trace)

    return data

  def extractBugsPerAssignee(self):
    """ 
      Generate a report of bugs per component. 
      Currently it only generates the bugs that are opened
    """
    print '\nGenerating classification of bugs per assignee grouped by resolution\n'
    data = self.extractBugsPerAssigneeOf(self.bugs['all'])

    return data