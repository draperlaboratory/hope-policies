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
import signal
import policy_test_common

# If the last test didn't end cleanly, we need to push the bitstream again
push_bitstream = True

# in this function, a set of policy test parameters is checked
#   to make sure that the test makes sense. If it doesnt, the
#   function returns the reason why
def incompatibleReason(test, policies, arch):
    # skip negative tests that are not matched to the correct policy
    if "ripe" not in test and "/" in test and (not test.split("/")[0] in policies):
        return "incorrect policy to detect violation in negative test"
    if "ppac" in policies and not all(policy in ["heap", "ppac", "userType"] for policy in policies):
        return "PPAC policy must run with heap and userType policies"
    return None

def xfailReason(test, runtime, policies, global_policies, arch):
    if test == "hello_works_2" and "testContext" in policies and not "contextswitch" in global_policies:
        return "hello_works_2 should fail with testContext unless the contextswitch policy is also there."
    if test == "float_works" and "heap" in policies and runtime == "frtos":
        return "float_works on FreeRTOS is known to fail with the heap policy."
    if test == "inline_asm_works_1" and ("cfi" in policies or runtime == "bare" and "threeClass" in policies):
        return "tagging of inline assembly is currently broken."
    return None


def testPath(runtime, soc, test):
    return os.path.join("build", runtime, soc, test)

# test function found automatically by pytest. Pytest calls
#   pytest_generate_tests in conftest.py to determine the
#   arguments. If they are parameterized, it will call this
#   function many times -- once for each combination of
#   arguments
def test_new(test, runtime, policy, global_policy, sim, rule_cache, rule_cache_size, debug, soc, timeout, arch, extra, output_subdir=None):
    policies = policy.split("-")
    global_policies = global_policy.split("-")
    global_policies = list(filter(None, global_policies))

    incompatible = incompatibleReason(test, policies, arch)
    if incompatible:
        pytest.skip(incompatible)

    xfail = xfailReason(test, runtime, policies, global_policies, arch)

    output_dir = os.path.abspath(os.path.join("output", arch))
    if output_subdir is not None:
        output_dir = os.path.join(output_dir, output_subdir)

    policy_name = policy_test_common.policyName(policies, global_policies, debug)
    policy_dir = os.path.abspath(os.path.join("policies", policy_name))

    pex_dir = os.path.abspath(os.path.join("pex", soc))
    
    pex_path = os.path.join(pex_dir, policy_test_common.pexName(soc, sim, policies, global_policies, "rv", debug))

    test_path = testPath(runtime, soc, test)

    runTest(test_path, runtime, policy_dir, pex_path, sim, rule_cache, rule_cache_size, output_dir, soc, timeout, arch, extra)

    test_output_dir = os.path.join(output_dir, "-".join(["isp", "run", os.path.basename(test), policy_name]))

    if rule_cache != "":
        test_output_dir = test_output_dir + "-{}-{}".format(rule_cache, rule_cache_size)

    # add policy-specific directory test source is in to output dir
    exe_dir = os.path.basename(os.path.dirname(os.path.dirname(test_path)))
    if exe_dir is not "tests":
        test_output_dir = test_output_dir + "-" + exe_dir

    testResult(test_output_dir, xfail)


def runTest(test, runtime, policy, pex, sim, rule_cache, rule_cache_size, output_dir, soc, timeout, arch, extra):
    global push_bitstream
    run_cmd = "isp_run_app"
    run_args = [test, soc, "-p", policy, "--pex", pex, "-s", sim, "-r", runtime, "-o", output_dir]
    if rule_cache != "":
        run_args += ["-C", rule_cache, "-c", rule_cache_size]

    if extra:
        extra_args = extra.split(",")
        if not push_bitstream:
            run_args += ["-e"] + list(filter(lambda arg: not "bitstream" in arg, extra_args))
        else:
            run_args += ["-e"] + extra_args
            push_bitstream = False

    # add policy-specific directory test source is in to output dir
    exe_dir = os.path.basename(os.path.dirname(os.path.dirname(test)))
    if exe_dir is not "tests":
        run_args += ["-S", exe_dir]

    failed_msg = ""
#    try:
        # Using PIPE for stdout sometimes prevents isp_run_app from noticing that the
        # process has ended. None won't hang, but will print `isp_run_app`s stdout.
        # DEVNULL hides the output and doesn't hang.

        # the run_cmd (e.g. the parent process) will spawn multiple children subprocesses - to ensure that they
        # can be killed when their parent exits (due to a time out), make sure that you associate a new session id to
        # the parent (e.g. run_cmd) process. That will make the parent the group leader of all the processes it (recursively) spawns
        # So now, when a signal is sent to the process group leader, it's transmitted to all of the child processes of this group.
    process = subprocess.Popen([run_cmd] + run_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
    try:
        outs, errs = process.communicate(timeout=timeout)
    except subprocess.CalledProcessError as err:
        failed_msg = "Test errored out with error code: {}\n".format(err.returncode)
        push_bitstream = True
    except subprocess.TimeoutExpired:
        failed_msg = "Test timed out\n"
        push_bitstream = True
        # parent timed out, kill all the children processes in the group
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)

    if failed_msg:
        pytest.fail(failed_msg + "\n".join(run_cmd) + "\n\twith args:\b" + "\n".join(run_args))


def testResult(test_output_dir,xfail):
    global push_bitstream
    uart_log_file = os.path.join(test_output_dir, "uart.log")   
    pex_log_file = os.path.join(test_output_dir, "pex.log")

    if not os.path.isdir(test_output_dir):
        pytest.fail("No test output directory {}".format(test_output_dir))
        return

    if not os.path.isfile(uart_log_file):
        # We get a false failure occasionally
        time.sleep(5)
        if not os.path.isfile(uart_log_file):
            pytest.fail("Simulator did not produce UART log file")
            return

    uart_data = open(uart_log_file, 'r', encoding='utf-8', errors='backslashreplace').read()

    if "PASS: test passed." not in uart_data:
        push_bitstream = True
        if "MSG: Negative test." in uart_data:
            message = open(pex_log_file, 'r').read()
            if any(s in message for s in ["Policy Violation", "TMT miss"]):
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
