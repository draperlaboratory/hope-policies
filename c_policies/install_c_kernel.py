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
This is a variant of isp_kernel.py that installs kernels for C language policies.
Currently this is hacking around the intended flow of DPL policies.
Usage is python install_c_kernel.py <policy-name> -o <kernel_out_dir>
'''

def copyEngineSources(engine_dir, output_dir):
    engine_output_dir = os.path.join(output_dir, "engine")
    isp_utils.doMkDir(engine_output_dir)

    shutil.copytree(os.path.join(engine_dir, "validator"), os.path.join(engine_output_dir, "validator"))
    shutil.copytree(os.path.join(engine_dir, "tagging_tools"), os.path.join(engine_output_dir, "tagging_tools"))
    shutil.copy(os.path.join(engine_dir, "Makefile.isp"), engine_output_dir)
    shutil.copy(os.path.join(engine_dir, "CMakeLists.txt"), engine_output_dir)

    shutil.copytree(os.path.join(engine_dir, "soc_cfg"), os.path.join(output_dir, "soc_cfg"))


def copyPolicyYaml(policy, policies_dir, entities_dir, output_dir):
    # Nick: this doesn't match with anything right now...
    policy_files = os.listdir(policies_dir)
    for policy_file in policy_files:
        if "yml" in policy_file or "log" in policy_file:
            print("Copying policy file " + policy_file)            
            shutil.copy(os.path.join(policies_dir, policy_file), output_dir)

    entities_source = os.path.join(entities_dir, policy + ".entities.yml")
    entities_dest = os.path.join(output_dir, policy + ".entities.yml")

    # special handling for composite policies
    # TODO: better way to determine composite policy?
    policy_parts = policy.split(".")[-1].split("-")
    policy_prefix = policy.rsplit(".", 1)[0] + "."

    print("Looking for " + entities_source)
    if os.path.isfile(entities_source):
        shutil.copy(entities_source, output_dir)

    # build composite entities for composite policy w.o existing entities
    elif (len(policy_parts) != 1):

        ents = []
        with open(entities_dest, 'w') as comp_ents:
            for p in policy_parts:

                policy_entities_file = policy_prefix + p + ".entities.yml"

                if os.path.isfile(os.path.join(entities_dir, policy_entities_file)):
                    f = os.path.join(entities_dir, policy_entities_file)
                    with open(f, "r") as instream:
                        for e in yaml.load_all(instream, Loader=yaml.FullLoader):
                            ents.append(e)

            if ents:
                yaml.dump_all(ents, comp_ents)

    if not os.path.isfile(entities_dest):
        shutil.copyfile(os.path.join(entities_dir, "empty.entities.yml"), entities_dest)

        
def copyPolicyToKernel(policy_src, policy_out_dir, kernel_dir):

    # Remove policy dir from that kernel
    shutil.rmtree(policy_out_dir, ignore_errors=True)

    # Copy policy in
    shutil.copytree(policy_src, policy_out_dir)

    # Copy yaml to top-level
    for policy_yaml in glob.glob(r"{}/policy_*.yml".format(policy_out_dir)):
        #print("Copying in " + policy_yaml)
        shutil.copy(policy_yaml, kernel_dir)
    
    return True

def buildPolicyKernel(policy, policies_dir, entities_dir, output_dir):
    engine_output_dir = os.path.join(output_dir, "engine")

    num_cores = str(multiprocessing.cpu_count())
    with open(os.path.join(output_dir, "build.log"), "w+") as buildlog:
        subprocess.Popen(["make", "-j"+num_cores, "-f", "Makefile.isp"], stdout=buildlog, stderr=subprocess.STDOUT, cwd=engine_output_dir).wait()
        subprocess.Popen(["make", "-j"+num_cores, "-f", "Makefile.isp install"], stdout=buildlog, stderr=subprocess.STDOUT, cwd=engine_output_dir).wait()

    validator_path = os.path.join(engine_output_dir, "build", "librv32-renode-validator.so")
    if not os.path.isfile(validator_path):
        return False

    shutil.move(validator_path, output_dir)
    #shutil.rmtree(engine_output_dir)

    return True


def main():
    parser = argparse.ArgumentParser(description="Build and install ISP kernels with policies")
    parser.add_argument("policy", type=str, help='''
    The name of the policy to compile and install
    ''')
    parser.add_argument("-o", "--output", type=str, default="", help='''
    Directory where the compiled pex kernel is stored
    Default is ISP_PREFIX/kernels or current working directory if ISP_PREFIX is not set
    ''')
    parser.add_argument("-d", "--debug", action="store_true", help='''
    Enable debug logging
    ''')

    args = parser.parse_args()

    isp_prefix = isp_utils.getIspPrefix()
    policies_dir = os.path.join(isp_prefix, "sources", "policies")
    engine_dir = os.path.join(isp_prefix, "sources", "policy-engine")
    policy_out_dir = os.path.join(engine_dir, "policy")
    soc_cfg_path = os.path.join(engine_dir, "soc_cfg")
    entities_dir = os.path.join(policies_dir, "entities")

    base_output_dir = os.getcwd()

    # policy should not have "/" at the end, remove if present
    if args.policy[-1] == "/":
        args.policy = args.policy[:-1]

    if args.output == "":
        kernels_dir = isp_utils.getKernelsDir()
        if os.path.isdir(kernels_dir):
            base_output_dir = kernels_dir
    else:
        base_output_dir = args.output

    kernel_name = "osv.frtos.main." + args.policy
    output_dir = os.path.abspath(os.path.join(base_output_dir, kernel_name))

    

    print("Building policy " + args.policy + ", kernel directory=" + args.output)
          
    shutil.rmtree(output_dir, ignore_errors=True)
    isp_utils.doMkDir(output_dir)
    print("making kernel dir=" + output_dir)

    print("Copying in engine...")
    copyEngineSources(engine_dir, output_dir)

    print("Copy entities...")
    copyPolicyYaml(kernel_name, policies_dir, entities_dir, output_dir)

    print("Copy in policy source...")
    policy_src = os.path.join(policies_dir, "c_policies", args.policy)
    policy_dest = os.path.join(output_dir, "engine", "policy")
    copyPolicyToKernel(policy_src, policy_dest, output_dir)
    
    if buildPolicyKernel(args.policy, policies_dir, entities_dir, output_dir) is False:
        print("Failed to build policy kernel. Run \"make -f Makefile.isp\" in /policy-engine or kernel for more info.")
        sys.exit(1)
    print("Succeeded build kernel.")


if __name__ == "__main__":
    main()
