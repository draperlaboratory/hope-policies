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

def pexName(sim, policy, debug):
    name = None

    if sim == "qemu":
        if debug:
            name = "-".join(["rv32", policy, "debug", "validator.so"])
        else:
            name = "-".join(["rv32", policy, "validator.so"])
    if sim == "vcu118":
        name = "-".join(["kernel", policy])
        if debug:
            name = "-".join(name, "debug")

    return name


# function found automatically by pytest
def test_install_policy(policy, global_policies, sim, debug):
    policies = policy.split("-")

    if "none" in global_policies:
        global_policies.remove("none")

    if not policy:
        pytest.fail("No policy specified")

    # split up policies from global policies for arg passing
    global_policies = [policy for policy in policies if policy in global_policies]
    policies = [policy for policy in policies if policy not in global_policies]

    policy_install_path = "policies"
    pex_install_path = os.path.join("pex", sim)

    pex_name = pexName(sim, policy, debug)
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
