# test script for running unit test

import pytest
import functools
import itertools
import operator
import subprocess
import os
import shutil
import time
import glob
import errno

import isp_run

# in this function, a set of policy test parameters is checked
#   to make sure that the test makes sense. If it doesnt, the
#   function returns the reason why
def incompatible_reason(test, policy, sim):

    # skip negative tests that are not matched to the correct policy
    if "/" in test and (not test.split("/")[0] in policy):
        return "incorrect policy to detect violation in negative test"
    
    return None

def xfail_reason(test, policy, sim):

    if "threeClass" in policy and "coremark" in test:
        return "threeClass and coremark; known unsolved bug"

    if "longjump" in test:
        return "longjump test known to be broken"

    return None

# test function found automatically by pytest. Pytest calls
#   pytest_generate_tests in conftest.py to determine the
#   arguments. If they are parameterized, it will call this
#   function many times -- once for each combination of
#   arguments
def test_run(test, runtime, policy, sim, rc):

    # policy = string of policy to be run, i.e. osv.hifive.main.rwx
    # test   = string of test to be run, i.e. hello_world_1.c
    # sim    = string of simulator to be used
    # rc     = tuple, rc[0] = rule cache type string, rc[1] = rule cache size
    # runtime= WHAT RUNTIME THE TEST WAS COMPILED FOR
    #          --> do not confuse this with simulator
    
    # check for test validity
    incompatible = incompatible_reason(test, policy, sim)
    if incompatible:
        pytest.skip(incompatible)

    xfail = xfail_reason(test, policy, sim)
    if xfail:
        pytest.xfail(xfail)

    res = isp_run.run_sim(test, runtime, policy, sim, rc)

    if res != isp_run.retVals.SUCCESS:
        if isp_run.retVals.NO_BIN == res or isp_run.retVals.NO_POLICY == res:
            pytest.skip(res)
        else:
            pytest.fail(res)

    # evaluate results
    # TODO : isp should output the output dir name
    name = isp_run.test_name(test, runtime)
    dirPath = isp_run.t_directory(name)
    pol_dir_name = policy
    if rc[0] != '' and rc[1] != '':
        pol_dir_name = pol_dir_name + '-' + rc[0] + rc[1]

    pol_test_path = os.path.join(dirPath, pol_dir_name)

    fail = fail_reason(pol_test_path)
    if fail != None:
        pytest.fail(fail)

        
def fail_reason(dp):
    print("Checking result...")
    with open(os.path.join(dp,"uart.log"), "r") as ulogf, \
         open(os.path.join(dp,"pex.log"), "r")  as plogf:
        ulog = ulogf.read()
        plog = plogf.read()
        if "MSG: Positive test." in ulog:
            if "PASS: test passed." in ulog:
                return None
            elif "Policy Violation:" in plog:
                return "Policy violation for positive test"
        elif "MSG: Negative test." in ulog:
            if "MSG: Begin test." in ulog:
                if "Policy Violation:" in plog:
                    return None
                return "No policy violation found for negative test"
            return "Test begin message not found"
    return "Unknown error"
