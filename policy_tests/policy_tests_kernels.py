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

import isp_kernel

# Nothing to configure below this point

# function found automatically by pytest
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
    
    # make the policy
    isp_kernel.doMkPolicy(policy, debug)
    
    isp_kernel.doInstallPolicy(policy, installPath)

    # check for success
    if not os.path.isfile(os.path.join(installPath, "librv32-renode-validator.so")):
        pytest.fail("Failed to generate validator shared object")


