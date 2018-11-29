

def test_name(main, runtime):

    name = main
    if "/" in main: # deal with negative tests
        name = main.split("/")[-1]

    name += "." + runtime

    return name

def test_from_testname(testname):
    return testname.split(".")[:-1].join(".")
