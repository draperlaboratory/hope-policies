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


def outputDir(runtime, sim, arch):
    if is_64_bit_arch(arch):
        return os.path.join(os.path.abspath("build"), runtime + '64', sim)
    return os.path.join(os.path.abspath("build"), runtime, sim)


def test_copy_build_dir(test, runtime, sim, arch):
    if not runtime:
        pytest.fail("No target runtime provided")

    if not test:
        pytest.fail("No test provided to build")

    output_dir = os.path.join(outputDir(runtime, sim, arch), "src")
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    if len(os.path.dirname(test)) != 0:
        output_test_parent_dir = os.path.join(output_dir, os.path.dirname(test))

        if not os.path.isdir(output_test_parent_dir):
            os.mkdir(output_test_parent_dir)

    output_test_dir = os.path.join(output_dir, test)

    if os.path.isdir(output_test_dir):
        pytest.skip("Using previously copied build directory")

    os.mkdir(output_test_dir)

    shutil.copy(os.path.join("tests", "test.h"), output_test_dir)
    shutil.copy(os.path.join("tests", "test.c"), output_test_dir)
    shutil.copy(os.path.join("tests", "test_status.h"), output_test_dir)
    shutil.copy(os.path.join("tests", "test_status.c"), output_test_dir)

    if isMakefileTest(test):
        shutil.copytree(os.path.join("tests", test), os.path.join(output_test_dir, os.path.basename(test)))
        if "webapp" in test:
            shutil.copytree(os.path.join("tests", "webapp"), os.path.join(output_test_dir, "webapp"))
    else:
        shutil.copy(os.path.join("tests", "common.mk"), output_test_dir)
        shutil.copy(os.path.join("tests", "Makefile." + runtime), output_test_dir)
        shutil.copy(os.path.join("tests", test + ".c"), output_test_dir)

    subprocess.Popen(["isp_install_runtime", runtime, sim, "-b", output_test_dir]).wait()


# function automatically found by pytest
def test_build(test, runtime, sim, arch, extra_args=None, extra_env=None):
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

    output_dir = outputDir(runtime, sim, arch)

    output_subdir = os.path.join(output_dir, os.path.dirname(test))
    if not os.path.isdir(output_subdir):
        os.makedirs(output_subdir, exist_ok=True)

    output_test_dir = os.path.join(output_dir, "src", test)
    if isMakefileTest(test):
        output_test_dir = os.path.join(output_test_dir, os.path.basename(test))

    make_args = ["make", "-C", output_test_dir, "-f", makefile]
    if extra_args is not None:
        make_args += extra_args

    env = dict(os.environ, OUTPUT_DIR=output_dir)
    if not isMakefileTest(test):
        env['TEST'] = test
    if extra_env is not None:
        env.update(extra_env)

    log_basename = os.path.basename(test) + ".log"
    log_file = open(os.path.join(output_dir, "log", log_basename), 'w')
    
    result = subprocess.Popen(make_args, env=env, stdout=log_file, stderr=subprocess.STDOUT).wait()
    if result is not 0:
        pytest.fail("Build failed. Command: OUTPUT_DIR={} extra_env={} {}".format(output_dir, extra_env, make_args))
