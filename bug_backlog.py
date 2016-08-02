import json
import requests
import datetime
import time
from datetime import date
import plotly.plotly as py
import plotly.graph_objs as graph
from pprint import pprint

class Backlog:

  def __init__(self, status, resolutions, bugs, from_date):
    self.status = status
    self.resolutions = resolutions
    self.bugs = bugs
    self.from_date = from_date

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
    print self.from_date
    for day in range(0 , self.from_date[2]):
      # get the current day of the month
      currentDay = datetime.date(self.from_date[0], self.from_date[1], (day + 1))
      x.append(currentDay)

      # get the number of bugs in that day
      numberOfBugsInDay = self.countBugsOfDay(currentDay, bugs)
      y.append(numberOfBugsInDay)

      print 'In %s there were %s bugs' %(currentDay, numberOfBugsInDay)

    return graph.Scatter(x=x, y=y, name=status)

  def extractBugsPerDay(self):
    """ Generate a report of opened and closed bugs per day of a give bugzilla server """
    print '\nGenerating bug backlog\n'
    data = []
    for status in self.status:
      result = self.extractBugsPerDayOf(status, self.bugs[status])
      data.append(result)

    return data