#!/usr/bin/python3

import functools
import itertools
import operator
import subprocess
import os.path
import time
import glob
import shutil
import multiprocessing
import argparse
import sys
import isp_utils
import yaml

'''
This is a variant of isp_install_policy.py. Rather than running policy-tool like we do
to create a new policy, we just copy the C source code into the appropriate location.
'''

def installPolicy(source_dir, output_dir):
    
    # If it's there, delete it first
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # Then copy in fresh
    shutil.copytree(source_dir, output_dir)


def compilePex(policy_dir, pex_path, sim, arch, extra):
    print("Attempting to compile PEX binary")
    install_path = os.path.dirname(pex_path)
    args = ["isp_install_policy",
             "-p", policy_dir,
             "-s", sim,
             "--arch", arch,
             "-o", install_path]

    if extra:
        args += ["-e"] + extra

    print("Building PEX kernel with command: {}".format(" ".join(args)))
    result = subprocess.call(args)

    if result != 0:
        return False

    print("Successfully compiled missing PEX binary")
    return True

def main():
    parser = argparse.ArgumentParser(description="Install a C policy")
    parser.add_argument("policy", type=str, help='''
    The name of the policy to compile and install
    ''')
    args = parser.parse_args()

    isp_prefix = isp_utils.getIspPrefix()

    # policy should not have "/" at the end, remove if present
    if args.policy[-1] == "/":
        args.policy = args.policy[:-1]

    dest_dir = os.path.join(isp_prefix, "policies", args.policy)
    
    print("Installing " + args.policy + " to " + dest_dir)
        
    installPolicy(args.policy, dest_dir)

    pex_path = os.path.join(isp_prefix, "validator", "rv32-" + args.policy + "validator.so")

    compilePex(dest_dir, pex_path, "qemu", "rv32", None)


if __name__ == "__main__":
    main()
