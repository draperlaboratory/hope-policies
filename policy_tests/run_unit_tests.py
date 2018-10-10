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
import pdb

from setup_test import *
#TODO make these cmd-line options?
quick_opt = ["O2"]
more_opts = ["O1", "O3"]

# Nothing to configure below this point

# filter fn for removing negative test cases that will fail due to 
#     missing the necessary policy
def valid(pol, test):
    print(pol)
    if os.path.dirname(test) == '':
        return True
    elif os.path.dirname(test) in pol:
        return True
    else:
        return False

# data collection for performance profiling
class Profiler:

    def __init__(self):
        self.results = []

    def test(self, policy, main, opt):
        self.p = policy
        self.m = main
        self.o = opt

    def start(self, str):
        self.s=self.toInt(str)

    def end(self, str):
        e=self.toInt(str)
        self.results.append((self.p,self.m,self.o,self.s,e))

    def report(self):
        self.rpt = open("prof_results.log", "w")
        list(map(self.rptFmt, sorted(self.results, key=self.file_key)))
        self.rpt.close()

    def toInt(self, str):
        ls = str.split("time:")
        return float(ls[1])
    
    def rptFmt(self, res):
        (p,m,o,s,e) = res
        print(tName((p,m,o)), s, e, e-s, file=self.rpt)

    def file_key(self, p_m_o_s_e):
        (p,m,o,s,e) = p_m_o_s_e
        return m

# build list of test cases, skip tests where required policy is not included in tools
@pytest.yield_fixture(scope="session")
def simpleFiles(testFile, simpleF):
    if(valid(simpleF, testFile)):
       return testFile
    else:
       pytest.skip(testFile)

# build list of test cases from broken list, skip tests where required policy is not included in tools
@pytest.yield_fixture(scope="session")
def brokenFiles(brokenTestFile, simpleF):
    testFile = brokenTestFile
    if(valid(simpleF, testFile)):
       return testFile
    else:
       pytest.skip(testFile)

# build tools and kernel for the policy combination to be tested
@pytest.yield_fixture(scope="session")
def simpleF(simplePol):
    return simplePol[2]

# build tools and kernel for the policy combination to be tested
@pytest.yield_fixture(scope="session")
def fullF(fullPol):
    return fullPol[2]

# build list of test cases, skip tests where required policy is not included in tools
@pytest.yield_fixture(scope="session")
def fullFiles(testFile, fullF):
    if(valid(fullF, testFile)):
       return testFile
    else:
       pytest.skip(testFile)

# build list of test cases, skip tests where required policy is not included in tools
@pytest.yield_fixture(scope="session")
def profileFiles(profileTestFile, simpleF):
    testFile = profileTestFile
    if(valid(simpleF, testFile)):
       return testFile
    else:
       pytest.skip(testFile)

# set up performance profiler
@pytest.yield_fixture(scope="session")
def profileRpt():
    prof = Profiler()
    yield prof
    prof.report()

# test targets that can be run with py.test - k <target prefix>
@pytest.mark.parametrize("opt", quick_opt + more_opts)
def test_all(fullF, fullFiles, opt, profileRpt, sim, remove_passing):
    policyParams = []
    doTest(fullF,fullFiles,opt, profileRpt, policyParams, remove_passing, "fail", sim)

@pytest.mark.parametrize("opt", quick_opt)
def test_full(fullF, fullFiles, opt, profileRpt, sim, remove_passing):
    policyParams = []
    doTest(fullF,fullFiles,opt, profileRpt, policyParams, remove_passing, "fail", sim)

@pytest.mark.parametrize("opt", quick_opt)
def test_simple(simpleF, simpleFiles, opt, profileRpt, sim, remove_passing):
    policyParams = []
    doTest(simpleF,simpleFiles,opt, profileRpt, policyParams, remove_passing, "fail", sim)

#debug target always leaves test dir under debug dir
@pytest.mark.parametrize("opt", quick_opt)
def test_debug(fullF, fullFiles, opt, profileRpt, sim):
    policyParams = []
    doTest(fullF,fullFiles,opt, profileRpt, policyParams, False, "debug", sim)

#broken target always leaves test dir under debug dir
@pytest.mark.parametrize("opt", quick_opt)
def test_broken(simpleF, brokenFiles, opt, profileRpt, sim):
    policyParams = []
    doTest(simpleF,brokenFiles,opt, profileRpt, policyParams, False, "broken", sim)

#profile target always leaves test dir under debug dir
@pytest.mark.parametrize("opt", quick_opt)
def test_profile(profileF, profileFiles, opt, profileRpt, sim):
    policyParams = []
    doTest(profileF,profileFiles,opt, profileRpt, policyParams, False, "prof", sim)


# Test execution function
def doTest(policy, main,opt, rpt, policyParams, removeDir, outDir, simulator):
    name = tName((policy, main,opt))
    rpt.test(policy, main,opt)
    doMkDir(outDir)
    dirPath = os.path.join(outDir, name)
    doBinDir(dirPath)
    doMkApp(policy, dirPath, main, opt)
    doMakefile(policy, dirPath, main, opt, "")
    doReSc(policy, dirPath, simulator)
    doValidatorCfg(policy, dirPath)
    doSim(dirPath, simulator)
#    testOK = checkPolicy(dirPath, policy, rpt)
    testOK = checkResult(dirPath, policy, rpt)
    doCleanup(policy, testOK, dirPath, main, opt, removeDir)

def doMkDir(dir):
    try:
        if not os.path.isdir(dir):
            os.makedirs(dir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print("{} already exists\n".format(dir))
        else:
            raise


def doBinDir(dp):
    shutil.rmtree(dp, ignore_errors=True)
    os.makedirs(os.path.join(dp, "build"))

def is32os(targ):
    switch = {
        "RV32" : "--disable-64bit",
        "RV32pex" : "--disable-64bit"
    }
    return switch.get(targ, "")

def doMkApp(policy, dp, main, opt):
    if "dos" in policy:
        runit(dp, "", "cp", [os.path.join("template", "dos-mem.h"), os.path.join(dp, "mem.h")])
        runit(dp, "", "cp", [os.path.join("template", "dos.cmake"), os.path.join(dp, "CMakeLists.txt")])
    elif "frtos" in policy:
        runit(dp, "", "cp", [os.path.join("template", "frtos-mem.h"), os.path.join(dp, "mem.h")])
        runit(dp, "", "cp", [os.path.join("template", "frtos.cmake"), os.path.join(dp, "CMakeLists.txt")])
    elif "hifive" in policy:
        runit(dp, "", "cp", [os.path.join("template", "hifive-mem.h"), os.path.join(dp, "mem.h")])
        shutil.copytree(os.getenv("ISP_PREFIX")+"hifive_bsp", os.path.join(dp, "build/bsp"))
        makefile = os.path.join(dp, "build/Makefile")
        shutil.copy(os.path.join("template", "hifive.makefile"), makefile)
    else:
        pytest.fail("Unknown OS, can't copy app files")
    runit(dp, "", "cp", [os.path.join("template", "doverlib.h"), dp])
#    runit(dp, "", "cp", [os.path.join("template", "print.c"), dp])
    runit(dp, "", "cp", [os.path.join("template", "dover-os.c"), os.path.join(dp, "dos.c")])
    runit(dp, "", "cp", [os.path.join("template", "frtos.c"), os.path.join(dp, "frtos.c")])
    runit(dp, "", "cp", [os.path.join("template", "hifive.c"), os.path.join(dp, "hifive.c")])
    runit(dp, "", "cp", [os.path.join("template", "test.h"), dp])
    runit(dp, "", "cp", [os.path.join("template", "test_status.c"), dp])
    runit(dp, "", "cp", [os.path.join("template", "test_status.h"), dp])
    runit(dp, "", "cp", [os.path.join("template", "runFPGA.py"), dp])
    runit(dp, "", "cp", [os.path.join("template", "runRenode.py"), dp])
    runit(dp, "", "cp", [os.path.join("template", "runQEMU.py"), dp])
    runit(dp, "", "cp", [os.path.join("tests", main), os.path.join(dp, "test.c")])
    # create entity for file elements
    entDir = os.path.abspath("../entities")
    entFile = main + ".entities.yml"
    srcEnt = os.path.join(entDir, entFile)
    destEnt = os.path.join(dp, entFile.replace('/', '-'))
    if os.path.isfile(srcEnt):
        shutil.copyfile(srcEnt, destEnt)
    else:
        shutil.copyfile(os.path.join(entDir, "empty.entities.yml"), destEnt)
    

# Generate the makefile
def doMakefile(policy, dp, main, opt, debug):
    if "frtos" in policy:
        mf = frtosMakefile(policy, main, opt, debug)
    elif "hifive" in policy:
        mf = hifiveMakefile(policy, main, opt, debug)
    else:
        pytest.fail("Unknown OS, can't generate Makefile")

    print("Makefile: {}".format(dp))
    with open(os.path.join(dp,'Makefile'), 'w') as f:
        f.write(mf)

    # compile the test
    runit(dp, "", "make", ["-C", dp])
    # check that build succeeded
    assert os.path.isfile(os.path.join(dp, "build", "main"))
    # copy over support files
    runit(dp, "", "make", ["-C", dp, "inits"])
    # Check for tag information
    assert os.path.isfile(os.path.join(dp, "build", "main.taginfo"))
    assert os.path.isfile(os.path.join(dp, "build", "main.text"))
    assert os.path.isfile(os.path.join(dp, "build", "main.text.tagged"))

# Generate the makefile
def doReSc(policy, dp, simulator):
    if "dos" in policy:
        rs = rescScript(dp, policy)
    elif "frtos" in policy:
        rs = rescScript(dp, policy)
    elif "hifive" in policy:
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

def doSim(dp, mkTarg):
    runit(dp, "", "make", ["-C", dp, mkTarg])

def checkPolicy(dp, policy, rpt):
    print("Checking policy...")
    with open(os.path.join(dp,"test.log"), "r") as fh:
        searchlines = fh.readlines()
    for line in searchlines:
        if "init policies:" in line:
            pexPolicy = line.split(":")[-1].strip().lower()
            testPolicy = policy.lower()
            if testPolicy != pexPolicy:
                print("ERROR: Wrong policy {pex} != {test}".format(pex = pexPolicy, test = testPolicy))
                return False
            else:
                return True
    return False

def checkResult(dp, policy, rpt):
    print("Checking result...")
    with open(os.path.join(dp,"uart.log"), "r") as fh:
        searchlines = fh.readlines()
    searchlines = [line for line in searchlines if line != "\n"]
    for i, line in enumerate(searchlines):
        if "MSG: Positive test." in line:
            rpt.start(searchlines[i+1])
            for j, l in enumerate(searchlines[i:]):
                if "PASS: test passed." in l:
                    rpt.end(searchlines[i+j+1])
                    return True
        elif "MSG: Negative test." in line:
            for j, l1 in enumerate(searchlines[i:]):
                if "MSG: Begin test." in l1:
                    with open(os.path.join(dp,"pex.log"), "r") as sh:
                        statuslines = sh.readlines()
                        for l2 in statuslines:
                            if "Policy Violation:" in l2:
                                return True
    fh.close()
    return False #   User code did not produce correct result

# FIXME: The -d has become obsolete (I think)
def doCleanup(policy, testOK, dp, main, opt, removeDir):
    if testOK:
        if removeDir:
            runit(None, "", "rm", ["-rf", dp])
        else:
            doMakefile(policy, dp, main, opt, "-d")
    else:
        doMakefile(policy, dp, main, opt, "-d")
        pytest.fail("User code did not produce correct result")

# this way seems to have process sync issues
def runitCall(dp, path, cmd, args):
    runcmd = [os.path.join(path,cmd)] + args
    print(runcmd)
    if dp != None:
        se = open(os.path.join(dp,"build.log"), "a")
        so = open(os.path.join(dp,"test.log"), "a")
        rc = subprocess.call(runcmd, stderr=se, stdout=so)
        se.close()
        so.close()
    else:
        print(str(runcmd))
        rc = subprocess.call(runcmd)

def runit(dp, path, cmd, args):
    runcmd = [os.path.join(path,cmd)] + args
    print(runcmd)
    if dp != None:
        se = open(os.path.join(dp,"spike.log"), "a")
        so = open(os.path.join(dp,"test.log"), "a")
        rc = subprocess.Popen(runcmd, stderr=se, stdout=so)
        while rc.poll() is None:
            time.sleep(0.01)
        se.close()
        so.close()
    else:
        print(str(runcmd))
        rc = subprocess.Popen(runcmd)
        while rc.poll() is None:
            time.sleep(0.01)

# The makefile that is generated in the test dir for hifive bare-metal tests
def hifiveMakefile(policy, main, opt, debug):
    kernel_dir = os.path.join(os.getcwd(), 'kernel_dir')
    return """
PYTHON ?= python3

build/main: hifive.c test.c
	cd build && make

inits:
	cp -r {kernel_dir}/kernels/{policies} .
	gen_tag_info -d ./{policies} -t build/main.taginfo -b build/main -e ./{policies}/{policies}.entities.yml {main}.entities.yml

verilator:
	$(MAKE) -C $(DOVER_SOURCES)/dover-verilog/SOC/verif clean
	cp bl.vh $(DOVER_SOURCES)/dover-verilog/SOC/verif
	cp all.vh $(DOVER_SOURCES)/dover-verilog/SOC/verif
	$(MAKE) -C $(DOVER_SOURCES)/dover-verilog/SOC/verif TEST=unit_test TIMEOUT=50000000 FPGA=1 TRACE_START=50000000
	cp $(DOVER_SOURCES)/dover-verilog/SOC/verif/Outputs/unit_test/unit_test_uart0.log .
	cp $(DOVER_SOURCES)/dover-verilog/SOC/verif/Outputs/unit_test/unit_test_uart1.log .

fpga:
	$(PYTHON) runFPGA.py

renode:
	$(PYTHON) runRenode.py

renode-console:
	renode main.resc

qemu:
	$(PYTHON) runQEMU.py {policies}

qemu-console:
	$(PYTHON) runQEMU.py {policies} -d

gdb:
	riscv32-unknown-elf-gdb -q -iex "set auto-load safe-path ./" build/main

clean:
	rm -f *.o main.out main.out.taginfo  main.out.text  main.out.text.tagged main.out.hex *.log
""".format(opt=opt, debug=debug,
           main_src=main, main_bin=main.replace(".c", ""),
           main=main.replace('/', '-'),
           policies=policy, kernel_dir=kernel_dir)

# The makefile that is generated in the test dir for frtos tests
def frtosMakefile(policy, main, opt, debug):
    kernel_dir = os.path.join(os.getcwd(), 'kernel_dir')
    return """
PYTHON ?= python3

rtos: frtos.c
	cd build && cmake .. && make

inits:
	cp -r {kernel_dir}/kernels/{policies} .
	gen_tag_info -d ./{policies} -t build/main.taginfo -b build/main -e ./{policies}/{policies}.entities.yml {main}.entities.yml

verilator:
	$(MAKE) -C $(DOVER_SOURCES)/dover-verilog/SOC/verif clean
	cp bl.vh $(DOVER_SOURCES)/dover-verilog/SOC/verif
	cp all.vh $(DOVER_SOURCES)/dover-verilog/SOC/verif
	$(MAKE) -C $(DOVER_SOURCES)/dover-verilog/SOC/verif TEST=unit_test TIMEOUT=50000000 FPGA=1 TRACE_START=50000000
	cp $(DOVER_SOURCES)/dover-verilog/SOC/verif/Outputs/unit_test/unit_test_uart0.log .
	cp $(DOVER_SOURCES)/dover-verilog/SOC/verif/Outputs/unit_test/unit_test_uart1.log .

fpga:
	$(PYTHON) runFPGA.py

renode:
	$(PYTHON) runRenode.py

renode-console:
	renode main.resc

gdb:
	riscv32-unknown-elf-gdb -q -iex "set auto-load safe-path ./" build/main

socat:
	socat - tcp:localhost:4444

clean:
	rm -f *.o main.out main.out.taginfo  main.out.text  main.out.text.tagged main.out.hex *.log
""".format(opt=opt, debug=debug, main = main.replace('/', '-'),
           policies=policy, kernel_dir=kernel_dir)

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
sysbus LoadELF @{path}/build/main
sysbus.ap_core SetExternalValidator @{path}/{policies}/librv32-renode-validator.so @{path}/{policies}/validator_cfg.yml
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
sysbus.cpu SetExternalValidator @{path}/librv32-renode-validator.so @{path} @{path}/build/main.taginfo @{path}/{policies}/soc_cfg/hifive_e_cfg.yml
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

def doValidatorCfg(policy, dirPath):
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
           tagfile=os.path.join(os.getcwd(), dirPath, "build/main.taginfo"),
           soc_cfg=os.path.join(os.getcwd(), dirPath, policy, "soc_cfg", soc_cfg))

    with open(os.path.join(dirPath,'validator_cfg.yml'), 'w') as f:
        f.write(validatorCfg)

# Special formatting for the pytest-html plugin

@pytest.mark.optionalhook
def pytest_html_results_table_html(report, data):
#    if report.passed:
        del data[:]
        data.append(html.div('No log output captured.', class_='empty log'))
