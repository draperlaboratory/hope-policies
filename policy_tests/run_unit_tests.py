# test script for running unit test

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

from setup_test import *

# in this function, a set of policy test parameters is checked
#   to make sure that the test makes sense. If it doesnt, the
#   function returns the reason why
def incompatible_reason(policy, test, sim):

    # skip negative tests that are not matched to the correct policy
    if "/" in test and (not test.split("/")[0] in policy):
        return "incorrect policy to detect violation in negative test"

    # TODO: is this a runtime/simulator mixup? How to do this check without
    #   trusting the name of the policy?
    # for now, hifive runtime only runs on qemu sim & frtos on renode
    if sim == "qemu" and "hifive" not in policy:
        return "hifive bare-metal is the only runtime currently supported by qemu"
    if sim == "renode" and "frtos" not in policy:
        return "frtos is the only runtime currently supported by renode"
    
    return None

# test function found automatically by pytest. Pytest calls
#   pytest_generate_tests in conftest.py to determine the
#   arguments. If they are parameterized, it will call this
#   function many times -- once for each combination of
#   arguments
def test_new(policy, test, sim, rc):

    # policy = string of policy to be run, i.e. osv.hifive.main.rwx
    # test   = string of test to be run, i.e. hello_world_1.c
    # sim    = string of simulator to be used
    # rc     = tuple, rc[0] = rule cache type string, rc[1] = rule cache size
    
    # check for test validity
    incompatible = incompatible_reason(policy, test, sim)
    if incompatible != None:
        pytest.skip(incompatible)

    # TODO: sync folder names ie specify the rule cache config in folder name
        
    # TODO: there is a similar test naming routine in the build_unit_tests.py
    #   -> should be a fn that both modules call?
    #   -> should this module be passed the paths to the build output dirs
    #      instead of the test names alone?

    # make output directory for test run
    if "/" in test:
        name = test.split("/")[-1]
    else:
        name = test

    # check that this test build 
    dirPath = os.path.join("output", name)
    if not os.path.isfile(os.path.join(dirPath, "build", "main")):
        pytest.skip("no complete build found")

    # simulator-specific run options
    if "qemu" in sim:
        shutil.copy(os.path.join("template", "runQEMU.py"), dirPath)
    elif "renode" in sim:
        shutil.copy(os.path.join("template", "runRenode.py"), dirPath)
    else:
        shutil.copy(os.path.join("template", "runFPGA.py"), dirPath)

    # policy-specific stuff

    # TODO: is this the best way to do this?
    # name directory with cache info if cache is being used
    if rc[0] == '' or rc[1] == '':
        pol_dir_name = policy;
    else:
        pol_dir_name = policy + '-' + rc[0] + rc[1]
    pol_test_path = os.path.join(dirPath, pol_dir_name)
    doMkDir(pol_test_path)

    # retrieve policy
    # TODO: kernel_dir/kernels/ -> kernels/ ?
    subprocess.Popen(["cp", "-r", os.path.join(os.path.join(os.getcwd(), 'kernel_dir/kernels'), policy), pol_test_path], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT).wait()
    if not os.path.isdir(os.path.join(pol_test_path, policy)):
        pytest.fail("policy not found")
    
    # test-run-level makefile. ie make inits & make qemu
    doMakefile(policy, pol_test_path, test)

    # script for 
    doReSc(policy, pol_test_path, sim)

    # config validator including rule cache
    doValidatorCfg(policy, pol_test_path, rc[0], rc[1])

    # run tagging tools
    doMkDir(os.path.join(pol_test_path, "bininfo"))
    initlog = open(os.path.join(pol_test_path, "inits.log"), "w+")
    subprocess.Popen(["make", "inits"], stdout=initlog, stderr=subprocess.STDOUT, cwd=pol_test_path).wait()

    # Check for tag information
    if not os.path.isfile(os.path.join(pol_test_path, "bininfo", "main.taginfo")) or \
       not os.path.isfile(os.path.join(pol_test_path, "bininfo", "main.text"))    or \
       not os.path.isfile(os.path.join(pol_test_path, "bininfo", "main.text.tagged")):
       pytest.fail("tagging tools did not produce expected output")
    
    # run test
    simlog = open(os.path.join(pol_test_path, "sim.log"), "w+")
    subprocess.Popen(["make", sim], stdout=simlog, stderr=subprocess.STDOUT, cwd=pol_test_path).wait()

    # evaluate results
    fail = fail_reason(pol_test_path)
    if fail != None:
        pytest.fail(fail)

# Generate the makefile
def doMakefile(policy, dp, main):

    # TODO: merge hifive & qemu makefiles?
    if "frtos" in policy:
        mf = frtosMakefile(policy, main)
    elif "hifive" in policy:
        mf = hifiveMakefile(policy, main)
    else:
        pytest.fail("Unknown OS, can't generate Makefile")

    print("Makefile: {}".format(dp))
    with open(os.path.join(dp,'Makefile'), 'w') as f:
        f.write(mf)

# The makefile that is generated in the test dir for hifive bare-metal tests
def hifiveMakefile(policy, main):
    kernel_dir = os.path.join(os.getcwd(), 'kernel_dir')
    return """
PYTHON ?= python3

inits:
	gen_tag_info -d ./{p} -t bininfo/main.taginfo -b ../build/main -e ./{p}/{p}.entities.yml ../{main}.entities.yml

renode:
	$(PYTHON) runRenode.py

renode-console:
	renode main.resc

qemu:
	$(PYTHON) ../runQEMU.py {p}

qemu-console:
	$(PYTHON) ../runQEMU.py {p} -d

gdb:
	riscv32-unknown-elf-gdb -q -iex "set auto-load safe-path ./" ../build/main

clean:
	rm -rf *.o *.log bininfo/*
""".format(main=main.replace('/', '-'), p=policy)

# The makefile that is generated in the test dir for frtos tests
def frtosMakefile(policy, main):
    kernel_dir = os.path.join(os.getcwd(), 'kernel_dir')
    return """
PYTHON ?= python3

inits:
	gen_tag_info -d ./{p} -t bininfo/main.taginfo -b ../build/main -e ./{p}/{p}.entities.yml ../{main}.entities.yml

renode:
	$(PYTHON) ../runRenode.py

renode-console:
	renode main.resc

gdb:
	riscv32-unknown-elf-gdb -q -iex "set auto-load safe-path ./" build/main

socat:
	socat - tcp:localhost:4444

clean:
	rm -f *.o *.log bininfo/*
""".format(main = main.replace('/', '-'), p=policy)

        
def doMkDir(dir):
    try:
        if not os.path.isdir(dir):
            os.makedirs(dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise    

# Generate the makefile
def doReSc(policy, dp, simulator):
    if "renode" in simulator:
        rs = rescScript(dp, policy)
    elif "qemu" in simulator:
        rs = rescScriptHifive(dp, policy)
    else:
        pytest.fail("Unknown OS, can't generate Scripts")

    gs = gdbScriptQemu(dp) if simulator == "qemu" else gdbScript(dp)

    print("Renode Script: {}".format(dp))
    with open(os.path.join(dp,'main.resc'), 'w') as f:
        f.write(rs)
    print("GDB Script: {}".format(dp))
    with open(os.path.join(dp,'.gdbinit'), 'w') as f:
        f.write(gs)

def fail_reason(dp):
    print("Checking result...")
    with open(os.path.join(dp,"uart.log"), "r") as fh:
        searchlines = fh.readlines()
    searchlines = [line for line in searchlines if line != "\n"]
    for i, line in enumerate(searchlines):
        if "MSG: Positive test." in line:
            for j, l in enumerate(searchlines[i:]):
                if "PASS: test passed." in l:
                    return None
            with open(os.path.join(dp,"pex.log"), "r") as sh:
                statuslines = sh.readlines()
                for l2 in statuslines:
                    if "Policy Violation:" in l2:
                        return "Policy violation for positive test"
            return "unknown error for positive test"
        elif "MSG: Negative test." in line:
            for j, l1 in enumerate(searchlines[i:]):
                if "MSG: Begin test." in l1:
                    with open(os.path.join(dp,"pex.log"), "r") as sh:
                        statuslines = sh.readlines()
                        for l2 in statuslines:
                            if "Policy Violation:" in l2:
                                return None
            return "No policy violation found for negative test"

    return "Unknown error"

def rescScript(dir, policy):
    return """
mach create
machine LoadPlatformDescription @platforms/boards/dover-riscv-board.repl
sysbus.ap_core MaximumBlockSize 1
emulation CreateServerSocketTerminal 4444 "uart-socket"
connector Connect sysbus.uart1 uart-socket
#showAnalyzer sysbus.uart Antmicro.Renode.UI.ConsoleWindowBackendAnalyzer
#emulation CreateUartPtyTerminal "uart-pty" "/tmp/uart-pty"
#connector Connect sysbus.uart uart-pty
sysbus LoadELF @{path}/../build/main
sysbus.ap_core SetExternalValidator @{path}/{policies}/librv32-renode-validator.so @{path}/validator_cfg.yml
sysbus.ap_core StartGdbServer 3333
logLevel 1 sysbus.ap_core
sysbus.ap_core StartStatusServer 3344
""".format(path = os.path.join(os.getcwd(), dir), policies=policy)


def rescScriptHifive(dir, policy):
    return """
using sysbus
mach create
machine LoadPlatformDescription @platforms/cpus/sifive-fe310.repl
sysbus.cpu MaximumBlockSize 1
emulation CreateServerSocketTerminal 4444 "uart-socket"
connector Connect uart0 uart-socket
#showAnalyzer sysbus.uart Antmicro.Renode.UI.ConsoleWindowBackendAnalyzer
#emulation CreateUartPtyTerminal "uart-pty" "/tmp/uart-pty"
#connector Connect sysbus.uart uart-pty
sysbus LoadELF @{path}/build/main
sysbus Tag <0x10008000 4> "PRCI_HFROSCCFG" 0xFFFFFFFF
sysbus Tag <0x10008008 4> "PRCI_PLLCFG" 0xFFFFFFFF
cpu PC `sysbus GetSymbolAddress "vinit"`
cpu PerformanceInMips 320
sysbus.ap_core SetExternalValidator @{path}/{policies}/librv32-renode-validator.so @{path}/validator_cfg.yml
sysbus.cpu StartGdbServer 3333
logLevel 1 sysbus.cpu
sysbus.cpu StartStatusServer 3344
""".format(path = os.path.join(os.getcwd(), dir), policies=policy)

def gdbScript(dir):
    return """

define metadata
   help metadata
end

document metadata
Renode simulator commands:
   rstart   - renode start
   rquit    - renode quit
Metadata related commnads:
   pvm      - print violation message
   lre      - print last rule evaluation
   env-m    - get the env metadata
   reg-m n  - get register n metadata
   areg-m   - get all register metadata
   csr-m a  - get csr metadata at addr a
   mem-m a  - get mem metadata at addr a
Watchpoints halt simulation when metadata changes
   env-mw   - set watch on the env metadata
   reg-mw n - set watch on register n metadata
   csr-mw a - set watch on csr metadata at addr a
   mem-mw a - set watch on mem metadata at addr a
end

define pvm
   monitor sysbus.ap_core PolicyViolationMsg
end

document pvm
   Command to print last policy violation info
   Only captures the last violation info.
end

define lre
   monitor sysbus.ap_core RuleEvalLog
end

document lre
   Command to print last rule evaluation info
end

define rstart
   monitor start
end

define rquit
   monitor quit
end

define env-m
   monitor sysbus.ap_core EnvMetadata
end

document env-m
   get environment metadata
end

define reg-m
   monitor sysbus.ap_core RegMetadata $arg0
end

document reg-m
   get register metadata
end

define areg-m
   monitor sysbus.ap_core AllRegMetadata
end

document areg-m
   get all register metadata
end

define csr-m
   monitor sysbus.ap_core CsrMetadata $arg0
end
document csr-m
   get csr metadata at addr
end

define mem-m
   monitor sysbus.ap_core MemMetadata $arg0
end
document mem-m
   get mem metadata at addr
end

define env-mw
   monitor sysbus.ap_core EnvMetadataWatch true
end
document env-mw
   set watch on the env metadata
end

define reg-mw
   monitor sysbus.ap_core RegMetadataWatch $arg0
end
document reg-mw
   set watch on register metadata
end

define csr-mw
   monitor sysbus.ap_core CsrMetadataWatch $arg0
end
document csr-mw
   set watch on csr metadata at addr
end

define mem-mw
   monitor sysbus.ap_core MemMetadataWatch $arg0
end
document mem-mw
   set watch on mem metadata at addr
end



define hook-stop
   pvm
end

set confirm off
target remote :3333
break main
monitor start
continue
""".format(path = os.path.join(os.getcwd(), dir))


def gdbScriptQemu(dir):
    return """

define metadata
   help metadata
end

document metadata
Metadata related commnads:
   pvm      - print violation message
   env-m    - get the env metadata
   reg-m n  - get register n metadata
   csr-m a  - get csr metadata at addr a
   mem-m a  - get mem metadata at addr a
Watchpoints halt simulation when metadata changes
   env-mw   - set watch on the env metadata
   reg-mw n - set watch on register n metadata
   csr-mw a - set watch on csr metadata at addr a
   mem-mw a - set watch on mem metadata at addr a
end

define pvm
   monitor pvm
end

document pvm
   Command to print last policy violation info
   Only captures the last violation info.
end

define env-m
   monitor env-m
end

document env-m
   get environment metadata
end

define reg-m
   monitor reg-m
end

document reg-m
   get register metadata
end

define csr-m
   monitor csr-m $arg0
end
document csr-m
   get csr metadata at addr
end

define mem-m
   monitor mem-m $arg0
end
document mem-m
   get mem metadata at addr
end

define env-mw
   monitor env-mw
end
document env-mw
   set watch on the env metadata
end

define reg-mw
   monitor reg-mw $arg0
end
document reg-mw
   set watch on register metadata
end

define csr-mw
   monitor csr-mw $arg0
end
document csr-mw
   set watch on csr metadata at addr
end

define mem-mw
   monitor mem-mw $arg0
end
document mem-mw
   set watch on mem metadata at addr
end



define hook-stop
   pvm
end

set confirm off
target remote :3333
break main
continue
""".format(path = os.path.join(os.getcwd(), dir))

# TODO: fix pulling hifive from policy
def doValidatorCfg(policy, dirPath, rule_cache, rule_cache_size):
    if "hifive" in policy:
        soc_cfg = "hifive_e_cfg.yml"
    else:
        soc_cfg = "dover_cfg.yml"

    validatorCfg =  """\
---
   policy_dir: {policyDir}
   tags_file: {tagfile}
   soc_cfg_path: {soc_cfg}
""".format(policyDir=os.path.join(os.getcwd(), dirPath, policy),
           tagfile=os.path.join(os.getcwd(), dirPath, "bininfo/main.taginfo"),
           soc_cfg=os.path.join(os.getcwd(), dirPath, policy, "soc_cfg", soc_cfg))

    if (rule_cache):
        validatorCfg += """\
   rule_cache:
      name: {rule_cache_name}
      capacity: {rule_cache_size}
        """.format(rule_cache_name=rule_cache, rule_cache_size=rule_cache_size)

    with open(os.path.join(dirPath,'validator_cfg.yml'), 'w') as f:
        f.write(validatorCfg)
