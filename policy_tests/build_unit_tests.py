
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

def test_build_simple(testFile, sim):
    doBuild(testFile, "output", sim)

# Test execution function
def doBuild(main, outDir, simulator):

    # output directory (for all tests)
    doMkDir(outDir)

    # make output directory for _this_ test
    if "/" in main:
        name = main.split("/")[-1] + "." + simulator
    else:
        name = main + "." + simulator
    dirPath = os.path.join(outDir, name)
    if not os.path.isdir(dirPath):
        doMkDir(dirPath)
        
        # make policy-common test sources & tools
        doMkApp(simulator, dirPath, main)

        # make build dir for test
        doMkBuildDir(dirPath, simulator);

        # do the build
        subprocess.Popen(["make"], stdout=open(os.path.join(dirPath, "build/build.log"), "w+"), stderr=subprocess.STDOUT, cwd=dirPath).wait()
        # check that build succeeded
        assert os.path.isfile(os.path.join(dirPath, "build", "main"))


def doMkBuildDir(dp, simulator):

    # build directory is 1 per test
    build_dir = os.path.join(dp, "build")
    if os.path.isdir(build_dir):
        return

    # make test/build
    doMkDir(build_dir)

    # provide test/build makefile
    if "renode" in simulator:
        shutil.copy(os.path.join("template", "frtos.cmake"), os.path.join(build_dir, "CMakeLists.txt"))
    elif "qemu" in simulator:
        shutil.copy(os.path.join("template", "hifive.makefile"), os.path.join(build_dir, "Makefile"))
        shutil.copytree(os.getenv("ISP_PREFIX")+"/hifive_bsp", os.path.join(build_dir, "bsp"))
        
def doMkDir(dir):
    try:
        if not os.path.isdir(dir):
            os.makedirs(dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
        
def doMkApp(simulator, dp, main):

    # pytest code run wrappers
    if "qemu" in simulator:
        shutil.copy(os.path.join("template", "runQEMU.py"), dp)
    elif "renode" in simulator:
        shutil.copy(os.path.join("template", "runRenode.py"), dp)
    else:
        shutil.copy(os.path.join("template", "runFPGA.py"), dp)

    # destination sources dir contains c sources & headers 
    src_dir = os.path.join(dp, "srcs")
    doMkDir(src_dir)

    if os.path.isfile(os.path.join("tests", main)):
        shutil.copy(os.path.join("tests", main), src_dir)
    else:
        for f in os.listdir(os.path.join("tests", main)):
            shutil.copy(os.path.join("tests", main, f), src_dir)

    # runtime specific code 
#    if "dos" in policy:
#        shutil.copy(os.path.join("template", "dos-mem.h"), os.path.join(dp, "mem.h"))
#        shutil.copy(os.path.join("template", "dos.cmake"), os.path.join(dp, "CMakeLists.txt"))
#        shutil.copy(os.path.join("template", "doverlib.h"), dp)
#        shutil.copy(os.path.join("template", "dover-os.c"), os.path.join(dp, "dos.c"))
    if "renode" in simulator:
        shutil.copy(os.path.join("template", "frtos-mem.h"), os.path.join(src_dir, "mem.h"))
        shutil.copy(os.path.join("template", "frtos.c"), os.path.join(src_dir, "frtos.c"))
        shutil.copyfile(os.path.join("template", "test.cmakefile"), os.path.join(dp, "Makefile"))
    elif "qemu" in simulator:
        shutil.copy(os.path.join("template", "hifive-mem.h"), os.path.join(src_dir, "mem.h"))
        shutil.copy(os.path.join("template", "hifive.c"), os.path.join(src_dir, "hifive.c"))
        shutil.copyfile(os.path.join("template", "test.makefile"), os.path.join(dp, "Makefile"))
    else:
        pytest.fail("Unknown OS, can't copy app files")

    # generic test code 
    shutil.copy(os.path.join("template", "test.h"), src_dir)
    shutil.copy(os.path.join("template", "test_status.c"), src_dir)
    shutil.copy(os.path.join("template", "test_status.h"), src_dir)
    shutil.copy(os.path.join("template", "sifive_test.h"), src_dir)
        
    # create entity for file elements
    entDir = os.path.abspath("../entities")
    entFile = main + ".entities.yml"
    srcEnt = os.path.join(entDir, entFile)
    destEnt = os.path.join(dp, entFile.replace('/', '-'))
    if os.path.isfile(srcEnt):
        shutil.copyfile(srcEnt, destEnt)
    else:
        shutil.copyfile(os.path.join(entDir, "empty.entities.yml"), destEnt)
