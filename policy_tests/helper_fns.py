

def test_name(main, runtime):

    name = main
    if "/" in main: # deal with negative tests
        name = main.split("/")[-1]

    name += "." + runtime

    return name

def test_from_testname(testname):
    return testname.split(".")[:-1].join(".")

def doMkDir(dir):
    try:
        if not os.path.isdir(dir):
            os.makedirs(dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise    

