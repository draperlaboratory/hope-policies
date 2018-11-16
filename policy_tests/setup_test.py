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
