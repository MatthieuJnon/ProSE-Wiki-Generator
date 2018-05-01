import subprocess

def path_to_table(path, author):
    try :
        command ='svn log {} --search "{}" | grep -oE "r([0-9])\w* | #([0-9])\w*"'.format(path, author)
    except : 
        raise RuntimeError("error while trying to get the logs from svn, its likely that your are not connected to internet")
    raw_output_string = (subprocess.check_output(command, shell=True)).decode("utf-8") 
    clean = raw_formater(raw_output_string)
    return clean

def raw_formater(raw):
    one_line = ' '.join((raw.replace("\\n"," ")).split())  
    list_of_revision = one_line.split('r')
    return string_to_dict(list_of_revision)


def string_to_dict(revtask_list):
    task_and_revisions = {}
    for revision in revtask_list[1:]:
        a_revision_with_its_tasks = revision.split() 
        for task in a_revision_with_its_tasks[1:] :
            task_without_hash = task.replace("#","")
            if task_without_hash not in task_and_revisions :
                task_and_revisions[task_without_hash] = ['r'+a_revision_with_its_tasks[0]]
            else :
                task_and_revisions[task_without_hash].append('r'+a_revision_with_its_tasks[0])
    return task_and_revisions






