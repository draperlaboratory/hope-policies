# test script for running unit test

import functools
import itertools
import operator
import subprocess
import os
import shutil
import time
import glob
import multiprocessing

# Modify the test_cfg module to add policies and test cases:
from functools import reduce


# Nothing to configure below this point

# Generate a file name string
def fName(file):
    return file.replace('/', '_')

def fullK(modules, policies):
    r = []
    for o in modules:
        for p in permutePols(policies):
            r.append((o, p, pName(o,p)))
    return [x[2] for x in r if len(x[1]) == 1 or not "none" in x[2]]

def simpleK(modules, policies):

    # length of policy that has every member policy except none
    composite_len = len(policies)
    if "none" in policies:
        composite_len -= 1

    return [x for x in fullK(modules, policies) if len(x.split(".")[-1].split("-")) == 1 or len(x.split(".")[-1].split("-")) == composite_len]

# generate the permutations of policies to compose
def permutePols(polStrs):
    p = sorted(polStrs)
    # list of number of policies
    ns = list(range(1,len(p)+1))
    # list of combinations for each n
    combs = [list(map(sorted,itertools.combinations(p, n))) for n in ns]
    # flatten list
    return (reduce(operator.concat, combs, []))

# Generate a policy name string
def pName(os, pol):
    return os + "." + "-".join(pol)

def runit(dp, path, cmd, args):
    runcmd = [os.path.join(path,cmd)] + args
    print(runcmd)
    if dp != None:
        se = open(os.path.join(dp,"spike.log"), "a")
        so = open(os.path.join(dp,"test.log"), "a")
        rc = subprocess.Popen(runcmd, stderr=se, stdout=so)
        while rc.poll() is None:
            time.sleep(0.01)
        se.close()
        so.close()
    else:
        print(str(runcmd))
        rc = subprocess.Popen(runcmd)
        while rc.poll() is None:
            time.sleep(0.01)
