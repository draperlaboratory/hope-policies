# test script for running unit test

import functools
import itertools
import operator
import subprocess
import os.path
import time
import glob
import shutil
import multiprocessing

from isp_utils import *

def build_policy_kernel(policy, debug, policies_dir, entities_dir,
                        engine_dir, pol_out_dir):

    # TODO: Default /opt/isp policies, entities, engine dirs?

    ptcmd = "policy-tool"
    ptarg = ["-t", entities_dir, "-m", policies_dir, "-o", pol_out_dir] + [policy]

    if debug: # prepend debug flag/argument for policy tool
        ptarg.insert(0, "-d")
    
    shutil.rmtree(pol_out_dir, ignore_errors=True)
    os.makedirs(pol_out_dir)
    # faster if we trust cmake & don't clean, but that can leave you with stale .so file
    fnull = open(os.devnull, 'w')
    pe_build_dir = os.path.join(engine_dir, "build")
    subprocess.Popen(["make", "clean"], stdout=fnull, stderr=subprocess.STDOUT, cwd=pe_build_dir).wait()

    with open(os.path.join(pol_out_dir, "policy_tool.log"), "w+") as ptlog:
        subprocess.Popen([ptcmd]+ptarg, stdout=ptlog, stderr=subprocess.STDOUT, cwd=pol_out_dir).wait()

    num_cores = str(multiprocessing.cpu_count())
    with open(os.path.join(pol_out_dir, "build.log"), "w+") as buildlog:
        subprocess.Popen(["make", "-j"+num_cores], stdout=buildlog, stderr=subprocess.STDOUT, cwd=pe_build_dir).wait()
        
def install_policy(policy, out_dir, pol_dir, ent_dir, val_path, soc_cfg_path):

    # TODO: Default /opt/isp policies, entities, engine dirs?
    
    shutil.rmtree(out_dir, ignore_errors=True)
    doMkDir(out_dir)
    
    shutil.copy(val_path, out_dir)

    shutil.copytree(soc_cfg_path, os.path.join(out_dir, "soc_cfg"))

    f_names = os.listdir(pol_dir)
    for fn in f_names:
        if "yml" in fn or "log" in fn:
            shutil.copy(os.path.join(pol_dir, fn), out_dir)

    entFile = os.path.join(ent_dir, policy + ".entities.yml")
    destEnt = os.path.join(out_dir, policy + ".entities.yml")

    # special handling for composite policies
    # TODO: better way to determine composite pol?
    policy_parts = policy.split(".")[-1].split("-")
    policy_prefix = policy.rsplit(".", 1)[0] + "."

    if os.path.isfile(entFile):
        shutil.copy(entFile, out_dir)
    elif (len(policy_parts) != 1):

        # build composite entities for composite policy w.o existing entities

        # make new empty file 
        shutil.copyfile(os.path.join(ent_dir, "empty.entities.yml"), destEnt)

        # concatenate all other files
        with open(destEnt, 'wb') as comp_ents:
            for p in policy_parts:
                polEntFile = policy_prefix + p + ".entities.yml"
                if os.path.isfile(os.path.join(ent_dir, polEntFile)):
                    with open(os.path.join(ent_dir, polEntFile), 'rb') as fd:
                        shutil.copyfileobj(fd, comp_ents);
    else: 
        shutil.copyfile(os.path.join(ent_dir, "empty.entities.yml"), destEnt)
