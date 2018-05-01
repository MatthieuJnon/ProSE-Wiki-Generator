from redmine_api import getTasksTuple
from svn_summary import path_to_table
import json
import os


def loadParameters():
    parameters = json.load(open("./parameters.json"))
    return parameters

def walker(path, author, tasks):
    os.chdir(path)
    for directory in os.listdir():
        if directory not in [".svn", "wiki_gen","code"] :
            to_explore = os.path.join(path, directory)
            explored = path_to_table(to_explore, author)
            full_info = joiner(tasks, explored)
            to_file(full_info, directory)



def joiner(task_details, task_revisions):
    details_and_revs = [[]]
    for key in task_details:
        if key in task_revisions:
            str_key = "#" + str(key)
            one_task_full = task_details[key] + task_revisions[key]
            one_task_full.append(str_key)
            details_and_revs.append(one_task_full)
    return details_and_revs

def to_file(full_infos,name):
    with open("wiki_gen/"+name, 'a+') as wiki_table:
        for task in full_infos :
            str_task  = [str(e) for e in task]
            wiki_format = '|{}|'.format('|'.join(str_task))
            print(wiki_format, file = wiki_table)


def run():
    try:
        parameters = loadParameters()
    except (IOError, OSError) as e:
        print(e)
        print("There was an error while accessing parameters.json")
        quit()
    
    try:
        apiKey = parameters["api-key"]
        if len(apiKey) < 10:
            raise LookupError("looks like the apiKey was incorrectly set. Please check the field in parameters.json")
    except LookupError as e:
        print(e)
        print("The api-key field was not set in parameters.json")
        quit()
    
    try:
        # This returns a list of this form : {'30087': [6.0, 'Contrat'], '30287': [1.5, 'Rencontre client du 13/04/2018']}
        tasks = getTasksTuple(apiKey)
        walker(parameters['svn-path'],'GuillaumeTecher',tasks)
    except RuntimeError:
        print(e)
        quit()



run()

