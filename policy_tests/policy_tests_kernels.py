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

from policy_tests_utils import *

# Nothing to configure below this point

# function found automatically by pytest
def test_install_kernel(policy, debug):

    if not policy:
        pytest.fail("No policy specified");

    out_dir = os.path.join("kernels", policy)

    # TODO: take renode out of name of validator
    # do not remake kernel unneccesarily
    if os.path.isfile(os.path.join(out_dir, "librv32-renode-validator.so")):
        pytest.skip("Using previously compiled kernel")
    
    # build the policy (ie run the policy tool)
    repo_root = os.path.join('..', '..')
    pol_dir = os.path.join(repo_root, "policies")
    ent_dir = os.path.join(pol_dir, "entities")
    eng_dir = os.path.join(repo_root, "policy-engine")
    pol_out_dir = os.path.join(eng_dir, "policy")
    isp_kernel.build_policy_kernel(policy, debug, pol_dir, ent_dir, eng_dir,
                                   pol_out_dir)

    # install the  policy & supporting infrastructure
    validator = "librv32-renode-validator.so"
    val_path = os.path.join(eng_dir, "build", validator)
    soc_cfg_path = os.path.join(eng_dir, "soc_cfg");
    isp_kernel.install_policy(policy, out_dir, pol_out_dir, ent_dir,
                              val_path, soc_cfg_path)

    # check for success
    if not os.path.isfile(os.path.join(out_dir, validator)):
        pytest.fail("Failed to generate validator shared object")


