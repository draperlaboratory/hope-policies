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
import policy_test_common

# function found automatically by pytest
def test_install_policy(policy, global_policy, soc, sim, arch, debug, extra):
    policies = policy.split("-")
    global_policies = global_policy.split("-")
    global_policies = list(filter(None, global_policies))

    policy_install_path = "policies"
    pex_install_path = os.path.join("pex", sim)

    processor=None
    if extra:
        processor = policy_test_common.getExtraArg(extra, "processor")

    pex_name = policy_test_common.pexName(sim, policies, global_policies, arch, debug, processor=processor)
    if not pex_name:
        pytest.fail("invalid arguments to determine pex name")
    if os.path.exists(os.path.join(pex_install_path, pex_name)):
        pytest.skip("PEX binary already exists")

    args = (["isp_install_policy", "-p"] + policies + ["-s", sim, "--soc", soc, "-o", pex_install_path, "-O", policy_install_path])

    if global_policies:
        args += ["-P"] + global_policies

    if debug:
        args += ["-D"]

    if extra:
        args += ["-e"] + extra.split(",")

    install_policy_log_file = os.path.join(policy_install_path, "log",
            policy_test_common.policyName(policies, global_policies, debug) + ".log")
    install_policy_log = open(install_policy_log_file, "w")
    result = subprocess.call(args, stdout=install_policy_log, stderr=subprocess.STDOUT)
    install_policy_log.close()
    if result != 0:
        pytest.fail("Failed to install policy with command: {}".format(" ".join(args)))
