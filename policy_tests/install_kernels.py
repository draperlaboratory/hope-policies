# test script for running unit test

import pytest
import functools
import itertools
import operator
import subprocess
import os.path
import time
import glob

# Modify the test_cfg module to add policies and test cases:
from setup_test import *

# Nothing to configure below this point

def test_install_kernel(policy):

    # make the policy
    doMkPolicy(policy)
    
    installPath = os.path.join('kernel_dir', "kernels", policy)

    doInstallPolicy(policy, installPath)

    if not os.path.isfile(os.path.join(installPath, "librv32-renode-validator.so")):
        pytest.fail("failed to generate validator shared object")

def doMkPolicy(policy):
    repo_root = os.path.join('..', '..')
    mod_dir = os.path.join(repo_root, "policies")
    ent_dir = os.path.join(mod_dir, "entities")
    gen_dir = os.path.join(repo_root, "policy-engine", "policy")
    ptcmd = "policy-tool"

    ptarg = ["-t", ent_dir, "-m", mod_dir, "-o", gen_dir] + [policy]

    shutil.rmtree(gen_dir, ignore_errors=True)
    os.makedirs(gen_dir)
    # faster if we trust cmake & don't clean, but that can leave you with stale .so file
    fnull = open(os.devnull, 'w')
    pe_build_dir = os.path.join(repo_root, "policy-engine/build")
    subprocess.Popen(["make", "clean"], stdout=fnull, stderr=subprocess.STDOUT, cwd=pe_build_dir).wait()

    # TODO remove runits and put logs in better place
    runit(None, "", ptcmd, ptarg)
    num_cores = str(multiprocessing.cpu_count())
    runit(None, "", "make", ["-C", os.path.join(repo_root, "policy-engine/build"), "-j"+num_cores])

        
def doInstallPolicy(policy, installPath):
    repo_root = os.path.join('..', '..')
    f = "librv32-renode-validator.so"
    src = os.path.join(repo_root, "policy-engine", "build", f)
    dst = os.path.join(installPath, f)
    pol_dir = os.path.join(repo_root, "policy-engine", "policy")
    soc_src = os.path.join(repo_root, "policy-engine", "soc_cfg")
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
    entFile = os.path.join(entDir, policy + ".entities.yml")
    destEnt = os.path.join(installPath, policy + ".entities.yml")

    # special handling for composite policies
    # TODO: better way to determine composite pol?
    policy_parts = policy.split(".")[-1].split("-")
    policy_prefix = policy.rsplit(".", 1)[0] + "."

    if os.path.isfile(entFile):
        shutil.copyfile(entFile, destEnt)
    elif (len(policy_parts) != 1):

        # build composite entities for composite policy w.o existing entities

        # make new empty file 
        shutil.copyfile(os.path.join(entDir, "empty.entities.yml"), destEnt)

        # concatenate all other files
        with open(destEnt, 'wb') as comp_ents:
            for p in policy_parts:
                polEntFile = policy_prefix + p + ".entities.yml"
                if os.path.isfile(os.path.join(entDir, polEntFile)):
                    with open(os.path.join(entDir, polEntFile), 'rb') as fd:
                        shutil.copyfileobj(fd, comp_ents);
    else: 
        shutil.copyfile(os.path.join(entDir, "empty.entities.yml"), destEnt)
