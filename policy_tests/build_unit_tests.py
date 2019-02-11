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
import re

from helper_fns import *

# True when test has its own Makefile
def isMakefileTest(test):
    if os.path.isdir(os.path.join("tests", test)):
        return True
    return False


def isRipeTest(test):
    if test.split('/')[0] == "ripe":
        return True
    return False


# function automatically found by pytest
def test_build(test, runtime, extra_args=None, extra_env=None):
    if not runtime:
        pytest.fail("No target runtime provided")

    if not test:
        pytest.fail("No test provided to build")

    test_dir = "tests"

    if isMakefileTest(test):
        test_dir = os.path.join(test_dir, test)

    if isRipeTest(test):
        test_dir = os.path.join(test_dir, "ripe")

    makefile = "Makefile.{}".format(runtime)
    if not os.path.isfile(os.path.join(test_dir, makefile)):
        pytest.fail("Test Makefile not found: {}".format(os.path.join(test_dir, makefile)))

    output_dir = os.path.join(os.path.abspath("build"), runtime)
    output_subdir = os.path.join(output_dir, os.path.dirname(test))
    if not os.path.isdir(output_subdir):
        os.mkdir(output_subdir)

    make_args = ["make", "-C", test_dir, "-f", makefile]
    if extra_args is not None:
        make_args += extra_args

    env = dict(os.environ, OUTPUT_DIR=output_dir)
    if not isMakefileTest(test):
        env['TEST'] = test
    if extra_env is not None:
        env.update(extra_env)
    
    devnull = open(os.devnull, 'w')
    result = subprocess.Popen(make_args, env=env, stdout=devnull, stderr=subprocess.STDOUT).wait()
    if result is not 0:
        pytest.fail("Build failed. Command: OUTPUT_DIR={} extra_env={} {}".format(output_dir, extra_env, make_args))
