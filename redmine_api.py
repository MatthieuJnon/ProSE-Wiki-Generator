from redminelib import Redmine, exceptions
from pprint import pprint
import sys

redmine = 0


class ProgressBar:
    progress = 0

    def __init__(self, width, total_range):
        # width sets the width of the progress bar
        # total_range is the number of steps expected
        self.width = width
        self.range = total_range

    def init_bar(self):
        sys.stdout.write("[%s]" % (" " * self.width))
        self._set_cursor_to_start(self.width + 1)
        self.progress = 0

    def _set_cursor_to_start(self, steps):
        # steps is the number of steps required to set the cursor back to start
        sys.stdout.flush()
        sys.stdout.write("\b" * steps)

    def inc_bar(self):
        self.progress += 1
        # Converting to int rounds down the number
        to_print = int((self.progress/self.range) * self.width)
        if(to_print >= self.width):
            to_print = self.width
        else:
            sys.stdout.write("#" * to_print)
            sys.stdout.flush()
        self._set_cursor_to_start(to_print)


def checkIfGoodProject(project):
    if(project.name.startswith('SE 2019 équipe')):
        return True
    return False


def getCurrentUserId(redmine):
    return redmine.user.get('current').id


def createTimeTable(times, redmine):
    timeTable = {}
    user = getCurrentUserId(redmine)
    print("fetching logged time")
    progress_bar = ProgressBar(width=40, total_range=len(times))
    progress_bar.init_bar()

    for time in times:
        progress_bar.inc_bar()
        if(user == time.user.id):
            try:
                timeTable[str(time.issue.id)][0] += time.hours
            except KeyError:
                issue = redmine.issue.get(time.issue.id)
                try:
                    timeTable[str(time.issue.id)] = [time.hours,
                                                     issue.subject,
                                                     issue.fixed_version.name]
                except exceptions.ResourceAttrError:
                    timeTable[str(time.issue.id)] = [time.hours,
                                                     issue.subject,
                                                     None]
    return timeTable


def getProSeProject(redmine):
    try:
        product = list(filter(checkIfGoodProject, redmine.project.all()))[0]
    except IndexError:
        product = None
    assert(product != None)
    return product


def getTasksTuple(apiKey):
    tuple = []
    try:
        redmine = Redmine('http://prose.eseo.fr/redmine', key=apiKey)
        project = getProSeProject(redmine)
    except Exception as e:
        print(e)
        raise RuntimeError(
            "error while connecting to Redmine with the provided API")

    tuple = createTimeTable(project.time_entries, redmine)
    return tuple
