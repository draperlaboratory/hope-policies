import os
import errno

def policy_test_name(main, runtime):
    name = main
    if "/" in main: # deal with negative tests
        name = main.split("/")[-1]

    name += "." + runtime

    return name

def policy_test_directory(name):
    if not "ripe." in name:
        return os.path.join("output", name)
    else:
        return os.path.join("output", "ripe", name.split(".")[1])

def doMkDir(dir):
    try:
        if not os.path.isdir(dir):
            os.makedirs(dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise    
