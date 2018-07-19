# test script for running unit test

import functools
import itertools
import operator
import subprocess
import os
import shutil
import time
import glob

# Modify the test_cfg module to add policies and test cases:
from cfg_test import *


# Nothing to configure below this point

def fullK():
    r = []
    for o in os_modules():
        for p in permutePols(policies()):
            r.append((o, p, pName(o,p)))
    return filter(lambda x: len(x[1]) == 1 or not "none" in x[2], r)

def simpleK():
    return filter(lambda x: len(x[1]) == 1 or len(x[1]) == len(policies()) , fullK())

# generate the permutations of policies to compose
def permutePols(polStrs):
    p = sorted(polStrs)
    # list of number of policies
    ns = range(1,len(p)+1)
    # list of combinations for each n
    combs = map(lambda n:map(sorted,itertools.combinations(p, n)), ns)
    # flatten list
    return (reduce(operator.concat, combs, []))


# return third element of tuple
def trd(t):
    return t[2]

#
# helper to wrap in a tuple
#def wrap(item):
#    return (item,)

# Generate a policy name string
def pName(os, pol):
    return os.format(pol = "-".join(pol))

def doMkPolicy(osPol, params):
    repo_root = os.path.join('..', '..')
    polParam = [osPol[2]]
    mod_dir = os.path.join(repo_root, "policies")
    ent_dir = os.path.join(mod_dir, "entities")
    gen_dir = os.path.join(repo_root, "policy-engine", "policy")
    ptcmd = "policy-tool"

    ptarg = params + ["-d", "-t", ent_dir, "-m", mod_dir, "-o", gen_dir] + polParam 

    shutil.rmtree(gen_dir, ignore_errors=True)
    os.makedirs(gen_dir)
# faster if we trust cmake & don't clean, but that can leave you with stale .so file
    runit(None, "", "make", ["-C", os.path.join(repo_root, "policy-engine/build"), "clean"])
    runit(None, "", ptcmd, ptarg)
    runit(None, "", "make", ["-C", os.path.join(repo_root, "policy-engine/build")])

def doInstallPolicy(osPol, installPath):
    repo_root = os.path.join('..', '..')
    polNm = osPol[2]
    f = "librv32-renode-validator.so"
    src = os.path.join(repo_root, "policy-engine", "build", f)
    dst = os.path.join(installPath, f)
    pol_dir = os.path.join(repo_root, "policy-engine", "policy")
    soc_src = os.path.join(repo_root, "policy-engine", "soc_cfg")
    if "hifive" in polNm:
        soc_src = soc_src.replace("soc_cfg", "soc_cfg_hifive")
    soc_dst = os.path.join(installPath, "soc_cfg")

    shutil.rmtree(installPath, ignore_errors=True)
    os.makedirs(installPath)
    shutil.copyfile(src, dst)
    shutil.copytree(soc_src, soc_dst)
    f_names = os.listdir(pol_dir)
    for fn in f_names:
        if "yml" in fn:
            shutil.copyfile(os.path.join(pol_dir, fn), os.path.join(installPath, fn))
    entDir = os.path.abspath("../entities")
    entFile = os.path.join(entDir, polNm + ".entities.yml")
    destEnt = os.path.join(installPath, polNm + ".entities.yml")
    if os.path.isfile(entFile):
        shutil.copyfile(entFile, destEnt)
    else:
        shutil.copyfile(os.path.join(entDir, "empty.entities.yml"), destEnt)

def installTarget(osPol):
    if osPol[0] == "dos":
        return "install-kernel"
    if osPol[0] == "frtos":
        return "install-no-kernel"
    pytest.fail( "Unknown kernel for install target")
    return ""

def runit(dp, path, cmd, args):
    runcmd = [os.path.join(path,cmd)] + args
    print runcmd
    if dp != None:
        se = open(os.path.join(dp,"spike.log"), "a")
        so = open(os.path.join(dp,"test.log"), "a")
        rc = subprocess.Popen(runcmd, stderr=se, stdout=so)
        while rc.poll() is None:
            time.sleep(0.01)
        se.close()
        so.close()
    else:
        print (str(runcmd))
        rc = subprocess.Popen(runcmd)
        while rc.poll() is None:
            time.sleep(0.01)
