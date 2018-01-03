import json
import copy
import plotly.plotly as py
import plotly.graph_objs as graph
from pprint import pprint

class Assignee:

  def __init__(self, status, resolutions, bugs):
    self.status = status
    self.resolutions = resolutions
    self.bugs = bugs  
    self.assignees = dict()
    self.assigneesStatus = [] 
    self.assigneesResolutions = [] 
    self.preProcessBugsPerAssigneeAndStatus(self.bugs['all'])
   

  def extractBugsPerAssigneePerStatus(self):
    data_status = []
    status_list = self.status
    for developer in self.assignees:
      bugs_map = self.assignees[developer]
      print status_list
      status_count = [0] * len(status_list)
      for st in bugs_map:
        count = sum(len(bugs_map[st][res]) for res in bugs_map[st])
        status_count[status_list.index(st)] = count
      trace = graph.Bar(
          x=status_list, 
          y=status_count, 
          name=developer[0 : developer.index('@')])
      data_status.append(trace)
    return data_status
  
  def extractBugsPerStatusPerResolution(self):
    data_resolution = []
    resolution_list = self.resolutions
    resolution_list.append('NONE')
    for developer in self.assignees:
      bugs_map = self.assignees[developer]
      for status_pointer in bugs_map:
        resolution_count = [0] * len(resolution_list)
        for res in bugs_map[status_pointer]:
          count = len(bugs_map[status_pointer][res])
          resolution_count[resolution_list.index(res)] = count
        trace = graph.Bar(
            x=resolution_list, 
            y=resolution_count, 
            name=developer[0 : developer.index('@')]+'_'+status_pointer)
        data_resolution.append(trace)
    return data_resolution
    # assignees = []

    # ## Iterates over all the bugs in order to split them by the assignee
    # for bug in bugs:
    #   clean_bug = {
    #     "bug_id": json.dumps(bug['id']).strip('"'),
    #     "severity": json.dumps(bug['severity']).strip('"'),
    #     "resolution": json.dumps(bug['resolution']).strip('"'),
    #     "status": json.dumps(bug['status']).strip('"'),
    #     "assignee": json.dumps(bug['assigned_to']).strip('"')
    #   }
    #   name = clean_bug['assignee'][0 : clean_bug['assignee'].index('@')
    #   if name not in assignees:
    #     assignees.append(name)
    # data = []
    # for assignee in assignees:
    #   x = list(self.status)
    #   y = []

    # # Cleaning the dictionary, erasing all empty lists and sub-dictionaries of it
    # for dev in self.assignees:
    #   for a in self.assignees[dev].keys():
    #     for b in self.assignees[dev][a].keys():
    #         if len(self.assignees[dev][a][b]) == 0: self.assignees[dev][a].pop(b, None)
    #     if len(self.assignees[dev][a]) == 0: self.assignees[dev].pop(a, None)

  def getAssigneesDetails(self):
    return self.assignees
  def getStatusResolutionMap(self):
   # Generates a map of all possible bug status for all possible bug resolutions
   mapa = dict()
   for st in self.status:
       mapa[st] = dict()
       for res in self.resolutions:
           mapa[st][res] = list()
       mapa[st]['NONE'] = list()
   return mapa

  def preProcessBugsPerAssigneeAndStatus(self, bugs):
    self.assignees = dict()
    mapa_status = self.getStatusResolutionMap()

    ## Iterates over all the bugs in order to split them by the assignee
    for bug in bugs:
      clean_bug = {
        "bug_id": json.dumps(bug['id']).strip('"'),
        "severity": json.dumps(bug['severity']).strip('"'),
        "resolution": json.dumps(bug['resolution']).strip('"'),
        "status": json.dumps(bug['status']).strip('"'),
        "assignee": json.dumps(bug['assigned_to']).strip('"')
      }
      
      if clean_bug["assignee"] not in self.assignees:
        self.assignees[clean_bug["assignee"]] = copy.deepcopy(mapa_status)
      firstIndex = clean_bug['status']
      secondIndex = clean_bug['resolution'] if clean_bug['resolution'] != "" else "NONE"
      self.assignees[clean_bug["assignee"]][firstIndex][secondIndex].append(clean_bug['bug_id'])

    # Cleaning the dictionary, erasing all empty lists and sub-dictionaries of it
    for dev in self.assignees:
      for a in self.assignees[dev].keys():
        for b in self.assignees[dev][a].keys():
            if len(self.assignees[dev][a][b]) == 0: self.assignees[dev][a].pop(b, None)
        if len(self.assignees[dev][a]) == 0: self.assignees[dev].pop(a, None)

  
  def extractBugsPerAssigneeOf(self):
    print self.assignees
    # data = []
    # obj = self.assignees
    # bug_status = self.status
    
    
    # filter(lambda assignee: assignee['name'] == assigned_to, assignees)[0]

    # trace = graph.Bar(
    #   x=bug_status, 
    #   y=[bugs_verified, bugs_confirmed, bugs_resolved], 
    #   name=assignee['name'][0 : assignee['name'].index('@')])
    # data.append(trace)

    # return data
    # assignees = []
    
    # data = []
    
    # # Building up the bug list per assignee
    
      
    #   if not assigned_to in assignees:
    #     assignees.append(dict(name = assigned_to, bugs = [],))

    #   currently_assinged_to = filter(lambda assignee: assignee['name'] == assigned_to, assignees)[0]
    #   bugs = currently_assinged_to['bugs']
      
    #   bugs.append(dict(bug_id=bugId, severity=bugSeverity, resolution=bugResolution, status= bugStatus))
    
    

    # # Mapping it to a pie-donut chart
    # bug_status = ['VERIFIED', 'CONFIRMED', 'RESOLVED']
    # bug_resolution = ['FIXED', 'DUPLICATE']
    
    # for assignee in assignees: 
    #   bugs_confirmed = sum(1 for bug in assignee['bugs'] if bug['status'] == 'CONFIRMED')
    #   bugs_resolved = sum(1 for bug in assignee['bugs'] if bug['status'] == 'RESOLVED')
    #   bugs_verified = sum(1 for bug in assignee['bugs'] if bug['status'] == 'VERIFIED')

    #   bugs_fixed = sum(1 for bug in assignee['bugs'] if bug['resolution'] == 'FIXED')
    #   bugs_dublicated = sum(1 for bug in assignee['bugs'] if bug['resolution'] == 'DUPLICATE')

    #   if not bugs_confirmed == 0 or not bugs_resolved == 0 or not bugs_verified == 0:
    #     total = bugs_confirmed + bugs_resolved + bugs_verified
    #     print '%s %s' %(assignee['name'][0 : assignee['name'].index('@')], total)
    #     print ' %s %s' %('verified', bugs_verified)
    #     print ' %s %s' %('confirmed', bugs_confirmed)
    #     print ' %s %s' %('resolved', bugs_resolved)
        
        # trace = graph.Bar(
        #   x=bug_status, 
        #   y=[bugs_verified, bugs_confirmed, bugs_resolved], 
        #   name=assignee['name'][0 : assignee['name'].index('@')])
        # data.append(trace)

    # return data
  
  def extractBugsPerAssignee(self):
    """ 
      Generate a report of bugs per component. 
      Currently it only generates the bugs that are opened
    """
    print '\nGenerating classification of bugs per assignee grouped by resolution\n'
    data = self.extractBugsPerAssigneeOf()

    return data