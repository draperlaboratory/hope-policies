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

def test_install_kernel(policy, debug, arch):
    if not policy:
        pytest.fail("No policy specified")

    install_path = os.path.join("kernels", arch, policy)
    if debug is True:
        install_path = "-".join([install_path, "debug"])
    if not os.path.isdir(install_path):
        os.makedirs(install_path)

    val_name = "".join(["lib", arch, "-renode-validator.so"])

    # do not remake kernel unneccesarily
    if os.path.isfile(os.path.join(install_path, val_name)):
        pytest.skip("Using previously compiled kernel")

    install_kernel_cmd = "isp_kernel"
    install_kernel_args = [policy, "-o", "kernels/{}".format(arch), "--arch", arch]
    if debug is True:
        install_kernel_args += ["-d"]

    subprocess.call([install_kernel_cmd] + install_kernel_args)

    if not os.path.isfile(os.path.join(install_path, val_name)):
        pytest.fail("Failed to generate validator shared object. Install path: {}".format(install_path))
