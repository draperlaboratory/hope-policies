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

from helper_fns import *

makefile_tests = [
    "coremark"
]

# function automatically found by pytest
def test_build(test, runtime):
    if not runtime:
        pytest.fail("No target runtime provided")

    if not test:
        pytest.fail("No test provided to build")

    test_dir = "tests"
    if test in makefile_tests:
        test_dir = os.path.join("tests", test)

    makefile = "Makefile.{}".format(runtime)
    if not os.path.isfile(os.path.join(test_dir, makefile)):
        pytest.fail("Test Makefile not found")

    output_dir = os.path.abspath("build")
    output_subdir = os.path.join(output_dir, os.path.dirname(test))
    if not os.path.isdir(output_subdir):
        os.mkdir(output_subdir)

    output_file = os.path.join(output_dir, "-".join([test, runtime]))
    if os.path.isfile(output_file):
        pytest.skip("Using previously compiled test")

    make_args = ["make", "-C", test_dir, "-f", makefile]
    devnull = open(os.devnull, 'w')
    env = dict(os.environ, OUTPUT_DIR=output_dir)
    if test not in makefile_tests:
        env['TEST'] = test   

    result = subprocess.Popen(make_args, env=env, stdout=devnull, stderr=subprocess.STDOUT).wait()
    if result is not 0:
        pytest.fail("Build failed. Command: OUTPUT_DIR={} {}".format(output_dir, make_args))
