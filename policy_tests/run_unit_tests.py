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
import helper_fns

# in this function, a set of policy test parameters is checked
#   to make sure that the test makes sense. If it doesnt, the
#   function returns the reason why
def incompatibleReason(test, policy):
    # skip negative tests that are not matched to the correct policy
    if "/" in test and (not test.split("/")[0] in policy):
        return "incorrect policy to detect violation in negative test"
    return None

def xfailReason(test):
    if "longjump" in test:
        return "longjump test known to be broken"
    return None

# test function found automatically by pytest. Pytest calls
#   pytest_generate_tests in conftest.py to determine the
#   arguments. If they are parameterized, it will call this
#   function many times -- once for each combination of
#   arguments
def test_new(test, runtime, policy, sim, rule_cache):
    incompatible = incompatibleReason(test, policy)
    if incompatible:
        pytest.skip(incompatible)

    xfail = xfailReason(test)
    if xfail:
        pytest.xfail(xfail)

    output_dir = os.path.abspath("output")
    policy_dir = os.path.abspath(os.path.join("kernels", policy))
    test_path = os.path.abspath(os.path.join("build", runtime, test))

    runTest(test_path, runtime, policy_dir, sim, rule_cache, output_dir)
    
    test_output_dir = os.path.join(output_dir, "-".join(["isp", "run", os.path.basename(test), policy]))
    if rule_cache != "":
        test_output_dir = test_output_dir + "-{}-{}".format(rule_cache[0], rule_cache[1])

    testResult(test_output_dir)


def runTest(test, runtime, policy, sim, rule_cache, output_dir):
    run_cmd = "isp_run_app"
    run_args = [test, "-p", policy, "-s", sim, "-r", runtime, "-o", output_dir]
    if rule_cache != "":
        run_args += ["-C", rule_cache[0], "-c", rule_cache[1]]

    devnull = open(os.devnull, 'w')
    subprocess.Popen([run_cmd] + run_args, stdout=devnull, stderr=subprocess.STDOUT).wait()

def testResult(test_output_dir):
    uart_log_file = os.path.join(test_output_dir, "uart.log")   
    pex_log_file = os.path.join(test_output_dir, "pex.log")

    if not os.path.isdir(test_output_dir):
        pytest.fail("No test output directory {}".format(test_output_dir))
        return

    if not os.path.isfile(uart_log_file):
        pytest.fail("Simulator did not produce UART log file")
        return

    if not os.path.isfile(uart_log_file):
        pytest.fail("Simulator did not produce UART log file")
        return

    uart_data = open(uart_log_file, 'r').read()

    if "PASS: test passed." not in uart_data:
        if "MSG: Negative test." in uart_data:
            if "Policy Violation:" in open(pex_log_file, 'r').read():
                return
            pytest.fail("No policy violation in negative test")
        else:
            pytest.fail("Positive test failed")
