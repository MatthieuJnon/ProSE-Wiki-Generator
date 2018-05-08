from redmine_api import getTasksTuple
from svn_summary import path_to_table
import json
import os


def loadParameters():
    parameters = json.load(open("./parameters.json"))
    return parameters


def walker(path, author, tasks):
    os.chdir(path)
    used_keys=[]
    for directory in os.listdir():
        if directory not in [".svn", "wiki_gen"]:
            to_explore = os.path.join(path, directory)
            explored = path_to_table(to_explore, author)
            if (explored != None):
                full_info_and_used_keys = joiner(tasks, explored)
                to_file(full_info_and_used_keys[0], directory, path)
                used_keys.extend(full_info_and_used_keys[1])
    leftover = leftover_gatherer(tasks, used_keys)
    to_file(leftover, "leftovers", path)

def joiner(task_details, task_revisions):
    details_and_revs = [[]]
    used_keys=[]
    for key in task_details:
        if key in task_revisions:
            used_keys.append(key)
            a_line = wiki_line(key, task_details, task_revisions)
            details_and_revs.append(a_line)
    return [details_and_revs,used_keys]

def leftover_gatherer(task_details,used_keys):
    lines = [[]]
    for key in task_details:
        if key not in used_keys:
            a_line = wiki_line(key, task_details, None)
            lines.append(a_line)
    return lines


def wiki_line(key, task_details, task_revisions):
    str_key = "#" + str(key)
    try:
        str_of_revs = ", ".join(task_revisions[key])
    except (KeyError, TypeError):
        str_of_revs = " "
    one_task_full = task_details[key]
    one_task_full.extend((str_of_revs, str_key))
    return one_task_full


def to_file(full_infos, name, path):
    wiki_gen_dir = os.path.join(path, "wiki_gen")
    if not os.path.exists(wiki_gen_dir):
        os.makedirs(wiki_gen_dir)

    full_infos = full_infos[1:]
    with open("wiki_gen/"+name+".txt", 'w+') as wiki_table:
        total_hours = 0
        for task in full_infos:
            total_hours += task[0]
            str_task = [str(e) for e in task]
            wiki_format = '|{}|'.format('|'.join(str_task))
            print(wiki_format, file=wiki_table)
        print("total : {}".format(total_hours), file=wiki_table)


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
            raise LookupError(
                "looks like the apiKey was incorrectly set. Please check the field in parameters.json")
    except LookupError as e:
        print(e)
        print("The api-key field was not set in parameters.json")
        quit()

    try:
        # This returns a list of this form : {'30087': [6.0, 'Contrat','version'], '30287': [1.5, 'Rencontre client du 13/04/2018', 'version']}
        # the third field might be None if there is no version
        tasks = getTasksTuple(apiKey)
        walker(parameters['svn-path'], parameters['user-name'], tasks)
    except RuntimeError as e:
        print(e)
        quit()


run()
