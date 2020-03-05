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
def test_install_policy(policy, global_policy, sim, debug):
    policies = policy.split("-")
    global_policies = global_policy.split("-")
    global_policies = list(filter(None, global_policies))

    policy_install_path = "policies"
    pex_install_path = os.path.join("pex", sim)

    pex_name = policy_test_common.pexName(sim, policies, global_policies, debug)
    if not pex_name:
        pytest.fail("invalid arguments to determine pex name")
    if os.path.exists(os.path.join(pex_install_path, pex_name)):
        pytest.skip("PEX binary already exists")

    args = (["isp_install_policy", "-p"] + policies + ["-s", sim,
            "-o", pex_install_path, "-O", policy_install_path])

    if global_policies:
        args += ["-P"] + global_policies

    if debug:
        args += ["-D"]

    result = subprocess.call(args, stdout=open(os.devnull, 'wb'), stderr=subprocess.STDOUT)
    if result != 0:
        pytest.fail("Failed to install policy")
