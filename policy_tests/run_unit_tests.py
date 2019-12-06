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
    if "ripe" not in test and "/" in test and (not test.split("/")[0] in policy):
        return "incorrect policy to detect violation in negative test"
    if "ppac" in policy and policy not in ["osv.bare.main.heap-ppac-userType",
                                           "osv.frtos.main.heap-ppac-userType"]:
        return "PPAC policy must run with heap and userType policies"
    return None

def xfailReason(test, policy, runtime):
    if test in ["hello_works_2"] and "testContext" in policy and not "contextswitch" in policy:
        return "hello_works_2 should fail with testContext unless the contextswitch policy is also there."

    return None

# test function found automatically by pytest. Pytest calls
#   pytest_generate_tests in conftest.py to determine the
#   arguments. If they are parameterized, it will call this
#   function many times -- once for each combination of
#   arguments
def test_new(test, runtime, policy, sim, rule_cache, rule_cache_size, debug, soc, timeout, extra, output_subdir=None):
    incompatible = incompatibleReason(test, policy)
    if incompatible:
        pytest.skip(incompatible)

    xfail = xfailReason(test, policy, runtime)

    output_dir = os.path.abspath("output")
    if output_subdir is not None:
        output_dir = os.path.join(output_dir, output_subdir)

    policy_dir = os.path.abspath(os.path.join("kernels", policy))
    if debug is True:
        policy_dir = "-".join([policy_dir, "debug"])

    test_path = os.path.abspath(os.path.join("build", runtime, sim, test))

    runTest(test_path, runtime, policy_dir, sim, rule_cache, rule_cache_size,
            output_dir, soc, timeout, extra)
    
    test_output_dir = os.path.join(output_dir, "-".join(["isp", "run", os.path.basename(test), policy]))

    if debug is True:
        test_output_dir = "-".join([test_output_dir, "debug"])

    if rule_cache != "":
        test_output_dir = test_output_dir + "-{}-{}".format(rule_cache, rule_cache_size)

    # add policy-specific directory test source is in to output dir
    exe_dir = os.path.basename(os.path.dirname(test_path))
    if exe_dir is not "tests":
        test_output_dir = test_output_dir + "-" + exe_dir

    testResult(test_output_dir,xfail)


def runTest(test, runtime, policy, sim, rule_cache, rule_cache_size, output_dir, soc, timeout, extra):
    run_cmd = "isp_run_app"
    run_args = [test, "-p", policy, "-s", sim, "-r", runtime, "--soc", soc, "-o", output_dir]
    if rule_cache != "":
        run_args += ["-C", rule_cache, "-c", rule_cache_size]

    if extra:
        extra_args = extra.split(",")
        run_args += ["-e"] + extra_args

    # add policy-specific directory test source is in to output dir
    exe_dir = os.path.basename(os.path.dirname(test))
    if exe_dir is not "tests":
        run_args += ["-S", exe_dir]

    if timeout:
        process = subprocess.Popen(["timeout",str(timeout),run_cmd] + run_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen([run_cmd] + run_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    run_output,run_error = process.communicate()
    if process.returncode != 0:
        pytest.fail("Runtime failed with error: \n{}".format(run_error))


def testResult(test_output_dir,xfail):
    uart_log_file = os.path.join(test_output_dir, "uart.log")   
    pex_log_file = os.path.join(test_output_dir, "pex.log")

    if not os.path.isdir(test_output_dir):
        pytest.fail("No test output directory {}".format(test_output_dir))
        return

    if not os.path.isfile(uart_log_file):
        pytest.fail("Simulator did not produce UART log file")
        return

    uart_data = open(uart_log_file, 'r').read()

    if "PASS: test passed." not in uart_data:
        if "MSG: Negative test." in uart_data:
            if "Policy Violation:" in open(pex_log_file, 'r').read():
                if xfail:
                    pytest.fail(xfail)
                return
            else:
                if xfail:
                    pytest.xfail(xfail)
                else:
                    pytest.fail("No policy violation in negative test")
        elif "MSG: Positive test." in uart_data:
            if xfail:
                pytest.xfail(xfail)
            else:
                pytest.fail("Positive test failed")
        else:
            if xfail:
                pytest.xfail(xfail)
            else:
                pytest.fail("Invalid output in uart file{}".format(uart_data))
    elif xfail:
        pytest.fail("XFAIL test passed: "+xfail)
