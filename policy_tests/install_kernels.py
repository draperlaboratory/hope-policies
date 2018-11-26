# test script for running unit test

import pytest
import functools
import itertools
import operator
import subprocess
import os.path
import time
import glob
import shutil
import multiprocessing

# Nothing to configure below this point

# function found automatically by pytest
def test_install_kernel(policy, debug):

    # TODO: don't hardcode path?
    installPath = os.path.join("kernels", policy)
    if not os.path.isdir(installPath):
        os.makedirs(installPath)
    
    # do not remake kernel unneccesarily
    if os.path.isfile(os.path.join(installPath, "librv32-renode-validator.so")):
        pytest.skip("using previously compiled kernel")
    
    # make the policy
    doMkPolicy(policy, debug)
    
    doInstallPolicy(policy, installPath)

    # check for success
    if not os.path.isfile(os.path.join(installPath, "librv32-renode-validator.so")):
        pytest.fail("failed to generate validator shared object")

def doMkPolicy(policy, debug):
    repo_root = os.path.join('..', '..')
    mod_dir = os.path.join(repo_root, "policies")
    ent_dir = os.path.join(mod_dir, "entities")
    gen_dir = os.path.join(repo_root, "policy-engine", "policy")
    ptcmd = "policy-tool"

    ptarg = ["-t", ent_dir, "-m", mod_dir, "-o", gen_dir] + [policy]
    if debug: # prepend debug flag/argument for policy tool
        ptarg.insert(0, "-d")
    
    shutil.rmtree(gen_dir, ignore_errors=True)
    os.makedirs(gen_dir)
    # faster if we trust cmake & don't clean, but that can leave you with stale .so file
    fnull = open(os.devnull, 'w')
    pe_build_dir = os.path.join(repo_root, "policy-engine/build")
    subprocess.Popen(["make", "clean"], stdout=fnull, stderr=subprocess.STDOUT, cwd=pe_build_dir).wait()

    with open(os.path.join(gen_dir, "policy_tool.log"), "w+") as ptlog:
        subprocess.Popen([ptcmd]+ptarg, stdout=ptlog, stderr=subprocess.STDOUT, cwd=gen_dir).wait()

    num_cores = str(multiprocessing.cpu_count())
    with open(os.path.join(gen_dir, "build.log"), "w+") as buildlog:
        subprocess.Popen(["make", "-j"+num_cores], stdout=buildlog, stderr=subprocess.STDOUT, cwd=pe_build_dir).wait()
        
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
        if "yml" in fn or "log" in fn:
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
