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

import isp_build
from policy_tests_utils import *

# function automatically found by pytest
def test_build(test, runtime):

    if not runtime:
        pytest.fail("No target runtime provided")

    if not test:
        pytest.fail("No test provided to build")

    name = policy_test_name(test, runtime)
    out_dir = policy_test_directory(name)
    doMkDir(out_dir)

    src_dir = os.path.join(out_dir, "srcs")
    doMkDir(src_dir)
    
    test_path = os.path.join("tests", test)
    
    if os.path.isfile(test_path):
        shutil.copy(test_path, src_dir)
    elif os.path.isdir(test_path):
        for f in os.listdir(test_path):
            shutil.copy(os.path.join(test_path, f), src_dir)
    else:
        pytest.skip("No test found")
    
    # generic test code 
    shutil.copy(os.path.join("template", "test.h"), src_dir)
    shutil.copy(os.path.join("template", "test_status.c"), src_dir)
    shutil.copy(os.path.join("template", "test_status.h"), src_dir)
    shutil.copy(os.path.join("template", "sifive_test.h"), src_dir)

    # create entity for file elements
    entDir = os.path.abspath("../entities")
    entFile = test + ".entities.yml"
    srcEnt = os.path.join(entDir, entFile)
    destEnt = os.path.join(out_dir, entFile.replace('/', '-'))
    if os.path.isfile(srcEnt):
        shutil.copyfile(srcEnt, destEnt)
    else:
        shutil.copyfile(os.path.join(entDir, "empty.entities.yml"), destEnt)
    
    if os.path.isfile(os.path.join(out_dir, "build", "main")):
        pytest.skip("Test already compiled.")

    # do the build
    res = isp_build.do_build(src_dir, "template", runtime, out_dir, copy_src = False)

    if res != isp_build.retVals.SUCCESS:
        pytest.fail(res)
