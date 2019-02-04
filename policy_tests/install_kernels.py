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

def test_install_kernel(policy, debug):

    if not policy:
        pytest.fail("No policy specified");
    
    # TODO: don't hardcode path?
    installPath = os.path.join("kernels", policy)
    if not os.path.isdir(installPath):
        os.makedirs(installPath)
    
    # do not remake kernel unneccesarily
    if os.path.isfile(os.path.join(installPath, "librv32-renode-validator.so")):
        pytest.skip("Using previously compiled kernel")
    
    makePolicy(policy, installPath, debug)

    if not os.path.isfile(os.path.join(installPath, "librv32-renode-validator.so")):
        pytest.fail("Failed to generate validator shared object")


def makePolicy(policy, install_path, debug)
    install_kernel_cmd = "isp_kernel"
    install_kernel_args = [policy, install_path]
    if debug is True:
        install_kernel_args += ["-d"]

    subprocess.call([install_kernel_cmd] + install_kernel_args)
