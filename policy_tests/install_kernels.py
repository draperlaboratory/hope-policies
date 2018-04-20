# test script for running unit test

import pytest
import functools
import itertools
import operator
import subprocess
import os.path
import time
import glob

# Modify the test_cfg module to add policies and test cases:
from setup_test import *

# Nothing to configure below this point

# build tools and kernel for the policy combination to be tested
@pytest.fixture(params=fullK(), ids=map(trd, fullK()))
def fullF(request):
    doFixture(request.param, [])
    return request.param

# build tools and kernel for the policy combination to be tested
@pytest.fixture(params=simpleK(), ids=map(trd, simpleK()))
def simpleF(request):
    doFixture(request.param, [])
    return request.param


def test_full(fullF):
    policyParams = []
    doTest(fullF)

def test_simple(simpleF):
    policyParams = []
    doTest(simpleF)

# target for installing a single kernel
def test_kernel(fullF):
    policyParams = []
    doTest(fullF)

# Build toolchain and kernel for policies
def doFixture(cfg, policyParams):
    doMkPolicy(cfg, policyParams)
#    doMkOS(cfg)

def doTest(osPolicyF):
    installPath = os.path.join(os.environ['DOVER'], "kernels", osPolicyF[2])
    doInstallPolicy(osPolicyF, installPath)
    print "Checking install: " + installPath
    assert os.path.isfile(os.path.join(installPath, "librv32-renode-validator.so"))
#    if osPolicyF[0] == "dos":
#        assert os.path.isfile(os.path.join(installPath, "ap_kernel.rom"))
#    assert os.path.isfile(os.path.join(installPath, "pex.rom"))
#    assert os.path.isfile(os.path.join(installPath, "post_meta"))
#    assert os.path.isfile(os.path.join(installPath, "tag_name_resolver.so"))


