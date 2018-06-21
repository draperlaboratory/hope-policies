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

# Modify the test_cfg module to add policies and test cases:
from setup_test import *

# Nothing to configure below this point


# Generate a test name string from test tuple
def tName((pol,fil,opt)):
    return '-'.join([pol, fName(fil),opt])

# Generate a file name string
def fName(file):
    return file.replace('/', '_')

# Compute the list of tests, each specified by (test, opt)
def testConfigs(tests, opts):
    return list(itertools.product(tests, opts))

# filter fn for removing negative test cases that will fail due to 
#     missing the necessary policy
def valid(pol, test):
    print pol
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
        map(self.rptFmt, sorted(self.results, key=self.file_key))
        self.rpt.close()

    def toInt(self, str):
        ls = str.split("time:")
        return float(ls[1])
    
    def rptFmt(self, res):
        (p,m,o,s,e) = res
        print >> self.rpt ,  tName((p,m,o)), s, e, e-s

    def file_key(self,(p,m,o,s,e)):
        return m

# build list of test cases, skip tests where required policy is not included in tools
@pytest.fixture(scope="module", params=positive_tests()+negative_tests(), ids=map(fName, positive_tests()+negative_tests()))
def simpleFiles(request, simpleF):
    testFile = request.param
    if(valid(simpleF, testFile)):
       return testFile
    else:
       pytest.skip(testFile)

# build list of test cases from broken list, skip tests where required policy is not included in tools
@pytest.fixture(scope="module", params=broken_tests, ids=map(fName, broken_tests))
def brokenFiles(request, simpleF):
    testFile = request.param
    if(valid(simpleF, testFile)):
       return testFile
    else:
       pytest.skip(testFile)

# build tools and kernel for the policy combination to be tested
@pytest.fixture(scope="session", params=simpleK(), ids=map(trd, simpleK()))
def simpleF(request):
    return request.param[2]

# build tools and kernel for the policy combination to be tested
@pytest.fixture(scope="session", params=fullK(), ids=map(trd, fullK()))
def fullF(request):
    return request.param[2]

# build list of test cases, skip tests where required policy is not included in tools
@pytest.fixture(scope="module", params=positive_tests()+negative_tests(), ids=map(fName, positive_tests()+negative_tests()))
def fullFiles(request, fullF):
    testFile = request.param
    if(valid(fullF, testFile)):
       return testFile
    else:
       pytest.skip(testFile)

# build list of test cases, skip tests where required policy is not included in tools
@pytest.fixture(scope="module", params=profile_tests, ids=map(fName, profile_tests))
def profileFiles(request, simpleF):
    testFile = request.param
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
def test_all(fullF, fullFiles, opt, profileRpt):
    policyParams = []
    doTest(fullF,fullFiles,opt, profileRpt, policyParams, removePassing, "fail")

@pytest.mark.parametrize("opt", quick_opt)
def test_full(fullF, fullFiles, opt, profileRpt):
    policyParams = []
    doTest(fullF,fullFiles,opt, profileRpt, policyParams, removePassing, "fail")

@pytest.mark.parametrize("opt", quick_opt)
def test_simple(simpleF, simpleFiles, opt, profileRpt):
    policyParams = []
    doTest(simpleF,simpleFiles,opt, profileRpt, policyParams, removePassing, "fail")

#debug target always leaves test dir under debug dir
@pytest.mark.parametrize("opt", quick_opt)
def test_debug(fullF, fullFiles, opt, profileRpt):
    policyParams = []
    global removePassing
    removePassing = False
    doTest(fullF,fullFiles,opt, profileRpt, policyParams, False, "debug")

#broken target always leaves test dir under debug dir
@pytest.mark.parametrize("opt", quick_opt)
def test_broken(simpleF, brokenFiles, opt, profileRpt):
    policyParams = []
    global removePassing
    removePassing = False
    doTest(simpleF,brokenFiles,opt, profileRpt, policyParams, False, "broken")

#profile target always leaves test dir under debug dir
@pytest.mark.parametrize("opt", quick_opt)
def test_profile(profileF, profileFiles, opt, profileRpt):
    policyParams = []
    doTest(profileF,profileFiles,opt, profileRpt, policyParams, False, "prof")


# Test execution function
def doTest(policy, main,opt, rpt, policyParams, removeDir, outDir):
    name = tName((policy, main,opt))
    rpt.test(policy, main,opt)
    doMkDir(outDir)
    dirPath = os.path.join(outDir, name)
    doBinDir(dirPath)
    doMkApp(policy, dirPath, main, opt)
    doMakefile(policy, dirPath, main, opt, "")
    doReSc(policy, dirPath)
    doSim(dirPath, simulator)
#    testOK = checkPolicy(dirPath, policy, rpt)
    testOK = checkResult(dirPath, policy, rpt)
    doCleanup(policy, testOK, dirPath, main, opt, removeDir)

def doMkDir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)

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
    # generate empty file system
#    runit(dp, "", "make", ["-C", dp, "fs"])
    # compile the test
    runit(dp, "", "make", ["-C", dp])
    # copy over support files
    runit(dp, "", "make", ["-C", dp, "inits"])
    # check that build succeeded
    assert os.path.isfile(os.path.join(dp, "build", "main"))

# Generate the makefile
def doReSc(policy, dp):
    if "dos" in policy:
        rs = rescScript(dp)
        gs = gdbScript(dp)
    elif "frtos" in policy:
        rs = rescScript(dp)
        gs = gdbScript(dp)
    elif "hifive" in policy:
        rs = rescScriptHifive(dp)
        gs = gdbScript(dp)
    else:
        pytest.fail("Unknown OS, can't generate Scripts")

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
                print "ERROR: Wrong policy {pex} != {test}".format(pex = pexPolicy, test = testPolicy)
                return False
            else:
                return True
    return False

def checkResult(dp, policy, rpt):
    print("Checking result...")
    with open(os.path.join(dp,"uart.log"), "r") as fh:
        searchlines = fh.readlines()
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
    print runcmd
    if dp != None:
        se = open(os.path.join(dp,"build.log"), "a")
        so = open(os.path.join(dp,"test.log"), "a")
        rc = subprocess.call(runcmd, stderr=se, stdout=so)
        se.close()
        so.close()
    else:
        print (str(runcmd))
        rc = subprocess.call(runcmd)

def runit(dp, path, cmd, args):
    runcmd = [os.path.join(path,cmd)] + args
    print runcmd
    if dp != None:
        se = open(os.path.join(dp,"spike.log"), "a")
        so = open(os.path.join(dp,"test.log"), "a")
        rc = subprocess.Popen(runcmd, stderr=se, stdout=so)
        while rc.poll() is None:
            time.sleep(0.01)
        se.close()
        so.close()
    else:
        print (str(runcmd))
        rc = subprocess.Popen(runcmd)
        while rc.poll() is None:
            time.sleep(0.01)

# The makefile that is generated in the test dir for hifive bare-metal tests
def hifiveMakefile(policy, main, opt, debug):
    kernel_dir = os.path.join(os.getcwd(), 'kernel_dir')
    return """
build/main: hifive.c test.c
	cd build && make

inits:
	cp {kernel_dir}/kernels/{policies}/librv32-renode-validator.so .
	cp {kernel_dir}/kernels/{policies}/policy_group.yml .
	cp {kernel_dir}/kernels/{policies}/policy_init.yml .
	cp {kernel_dir}/kernels/{policies}/policy_meta.yml .
	cp {kernel_dir}/kernels/{policies}/entities.yml .
	cp -r {kernel_dir}/kernels/{policies}/soc_cfg .
	riscv32-unknown-elf-objdump --source build/main > build/main.text
	gen_tag_info -d {kernel_dir}/kernels/{policies} -t build/main.taginfo -b build/main -p {policies}
	md_entity {kernel_dir}/kernels/{policies} build/main build/main.taginfo {main}.entities.yml
	md_asm_ann {kernel_dir}/kernels/{policies} build/main.taginfo build/main.text


verilator:
	$(MAKE) -C $(DOVER_SOURCES)/dover-verilog/SOC/verif clean
	cp bl.vh $(DOVER_SOURCES)/dover-verilog/SOC/verif
	cp all.vh $(DOVER_SOURCES)/dover-verilog/SOC/verif
	$(MAKE) -C $(DOVER_SOURCES)/dover-verilog/SOC/verif TEST=unit_test TIMEOUT=50000000 FPGA=1 TRACE_START=50000000
	cp $(DOVER_SOURCES)/dover-verilog/SOC/verif/Outputs/unit_test/unit_test_uart0.log .
	cp $(DOVER_SOURCES)/dover-verilog/SOC/verif/Outputs/unit_test/unit_test_uart1.log .

fpga:
	python runFPGA.py

renode:
	python runRenode.py

renode-console:
	renode main.resc

qemu:
	python runQEMU.py

gdb:
	riscv32-unknown-elf-gdb -q -iex "set auto-load safe-path ./" build/main

clean:
	rm -f *.o main.out main.out.taginfo  main.out.text  main.out.text.tagged main.out.hex *.log
""".format(opt=opt, debug=debug,
           main_src=main, main_bin=main.replace(".c", ""),
           main=main.replace('/', '-'),
           policies=policy.lower(), kernel_dir=kernel_dir)

# The makefile that is generated in the test dir for frtos tests
def frtosMakefile(policy, main, opt, debug):
    kernel_dir = os.path.join(os.getcwd(), 'kernel_dir')
    return """
rtos: frtos.c
	cd build && cmake .. && make

inits:
	cp {kernel_dir}/kernels/{policies}/librv32-renode-validator.so .
	cp {kernel_dir}/kernels/{policies}/policy_group.yml .
	cp {kernel_dir}/kernels/{policies}/policy_init.yml .
	cp {kernel_dir}/kernels/{policies}/policy_meta.yml .
	cp {kernel_dir}/kernels/{policies}/entities.yml .
	cp -r {kernel_dir}/kernels/{policies}/soc_cfg .
	riscv32-unknown-elf-objdump --source build/main > build/main.text
	gen_tag_info -d {kernel_dir}/kernels/{policies} -t build/main.taginfo -b build/main -p {policies}
	md_entity {kernel_dir}/kernels/{policies} build/main build/main.taginfo {main}.entities.yml
	md_asm_ann {kernel_dir}/kernels/{policies} build/main.taginfo build/main.text

verilator:
	$(MAKE) -C $(DOVER_SOURCES)/dover-verilog/SOC/verif clean
	cp bl.vh $(DOVER_SOURCES)/dover-verilog/SOC/verif
	cp all.vh $(DOVER_SOURCES)/dover-verilog/SOC/verif
	$(MAKE) -C $(DOVER_SOURCES)/dover-verilog/SOC/verif TEST=unit_test TIMEOUT=50000000 FPGA=1 TRACE_START=50000000
	cp $(DOVER_SOURCES)/dover-verilog/SOC/verif/Outputs/unit_test/unit_test_uart0.log .
	cp $(DOVER_SOURCES)/dover-verilog/SOC/verif/Outputs/unit_test/unit_test_uart1.log .

fpga:
	python runFPGA.py

renode:
	python runRenode.py

renode-console:
	renode main.resc

gdb:
	riscv32-unknown-elf-gdb -q -iex "set auto-load safe-path ./" build/main

socat:
	socat - tcp:localhost:4444

clean:
	rm -f *.o main.out main.out.taginfo  main.out.text  main.out.text.tagged main.out.hex *.log
""".format(opt=opt, debug=debug, main = main.replace('/', '-'),
           policies=policy.lower(), kernel_dir=kernel_dir)

def rescScript(dir):
    return """
mach create
machine LoadPlatformDescription @platforms/boards/miv-board.repl
sysbus.cpu MaximumBlockSize 1
emulation CreateServerSocketTerminal 4444 "uart-socket"
connector Connect sysbus.uart uart-socket
#showAnalyzer sysbus.uart Antmicro.Renode.UI.ConsoleWindowBackendAnalyzer
#emulation CreateUartPtyTerminal "uart-pty" "/tmp/uart-pty"
#connector Connect sysbus.uart uart-pty
sysbus LoadELF @{path}/build/main
sysbus.cpu SetExternalValidator @{path}/librv32-renode-validator.so @{path} @{path}/build/main.taginfo
sysbus.cpu StartGdbServer 3333
logLevel 1 sysbus.cpu
sysbus.cpu StartStatusServer 3344
""".format(path = os.path.join(os.getcwd(), dir))


def rescScriptHifive(dir):
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
sysbus.cpu SetExternalValidator @{path}/librv32-renode-validator.so @{path} @{path}/build/main.taginfo
sysbus.cpu StartGdbServer 3333
logLevel 1 sysbus.cpu
sysbus.cpu StartStatusServer 3344
""".format(path = os.path.join(os.getcwd(), dir))

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
   monitor sysbus.cpu PolicyViolationMsg
end

document pvm
   Command to print last policy violation info
   Only captures the last violation info.
end

define rstart
   monitor start
end

define rquit
   monitor quit
end

define env-m
   monitor sysbus.cpu EnvMetadata
end

document env-m
   get environment metadata
end

define reg-m
   monitor sysbus.cpu RegMetadata $arg0
end

document reg-m
   get register metadata
end

define csr-m
   monitor sysbus.cpu CsrMetadata $arg0
end
document csr-m
   get csr metadata at addr
end

define mem-m
   monitor sysbus.cpu MemMetadata $arg0
end
document mem-m
   get mem metadata at addr
end

define env-mw
   monitor sysbus.cpu EnvMetadataWatch true
end
document env-mw
   set watch on the env metadata
end

define reg-mw
   monitor sysbus.cpu RegMetadataWatch $arg0
end
document reg-mw
   set watch on register metadata
end

define csr-mw
   monitor sysbus.cpu CsrMetadataWatch $arg0
end
document csr-mw
   set watch on csr metadata at addr
end

define mem-mw
   monitor sysbus.cpu MemMetadataWatch $arg0
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

# Special formatting for the pytest-html plugin

@pytest.mark.optionalhook
def pytest_html_results_table_html(report, data):
#    if report.passed:
        del data[:]
        data.append(html.div('No log output captured.', class_='empty log'))
