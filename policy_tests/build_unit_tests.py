
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

# function automatically found by pytest
def test_build(test, runtime):

    if not runtime:
        pytest.fail("No target runtime provided")

    if not test:
        pytest.fail("No test provided to build")

    do_build(test, "output", runtime)

def do_build(main, outDir, runtime):

    # output directory (for all tests)
    doMkDir(outDir)

    name = test_name(main, runtime)
    
    dirPath = t_directory(name)
    if os.path.isfile(os.path.join(dirPath, "build", "main")):
        pytest.skip("Test directory already exists: " + name)
    doMkDir(dirPath)

    # make policy-common test sources & tools
    doMkApp(runtime, dirPath, main)
    
    # make build dir for test
    doMkBuildDir(dirPath, runtime);
        
    # do the build
    subprocess.Popen(["make"], stdout=open(os.path.join(dirPath, "build/build.log"), "w+"), stderr=subprocess.STDOUT, cwd=dirPath).wait()

    # check that build succeeded
    if not os.path.isfile(os.path.join(dirPath, "build", "main")):
        pytest.fail("No binary produced. Log: " + dirPath + "/build/build.log")

def doMkBuildDir(dp, runtime):

    # build directory is 1 per test
    build_dir = os.path.join(dp, "build")
    if os.path.isdir(build_dir):
        return

    # make test/build
    doMkDir(build_dir)

    # provide test/build makefile
    if "frtos" in runtime:
        shutil.copy(os.path.join("template", "frtos.cmake"), os.path.join(build_dir, "CMakeLists.txt"))
    elif "hifive" in runtime:
        shutil.copy(os.path.join("template", "hifive.makefile"), os.path.join(build_dir, "Makefile"))
        shutil.copytree(os.getenv("ISP_PREFIX")+"/hifive_bsp", os.path.join(build_dir, "bsp"))
        
def doMkApp(runtime, dp, main):

    # destination sources dir contains c sources & headers 
    src_dir = os.path.join(dp, "srcs")
    doMkDir(src_dir)

    if os.path.isfile(os.path.join("tests", main)):
        shutil.copy(os.path.join("tests", main), src_dir)
    elif os.path.isdir(os.path.join("tests", main)):
        for f in os.listdir(os.path.join("tests", main)):
            shutil.copy(os.path.join("tests", main, f), src_dir)
    else:
        pytest.fail("Test not found: " + main);
        
    # runtime specific code 
    if "frtos" in runtime:
        shutil.copy(os.path.join("template", "frtos-mem.h"), os.path.join(src_dir, "mem.h"))
        shutil.copy(os.path.join("template", "frtos.c"), os.path.join(src_dir, "frtos.c"))
        shutil.copyfile(os.path.join("template", "test.cmakefile"), os.path.join(dp, "Makefile"))
    elif "hifive" in runtime:
        shutil.copy(os.path.join("template", "hifive-mem.h"), os.path.join(src_dir, "mem.h"))
        shutil.copy(os.path.join("template", "hifive.c"), os.path.join(src_dir, "hifive.c"))
        shutil.copyfile(os.path.join("template", "test.makefile"), os.path.join(dp, "Makefile"))
    else:
        pytest.fail("Target runtime not found: " + runtime)

    # generic test code 
    shutil.copy(os.path.join("template", "test.h"), src_dir)
    shutil.copy(os.path.join("template", "test_status.c"), src_dir)
    shutil.copy(os.path.join("template", "test_status.h"), src_dir)
    shutil.copy(os.path.join("template", "sifive_test.h"), src_dir)
        
    # create entity for file elements
    entDir = os.path.abspath("../entities")
    entFile = "main.entities.yml"
    srcEnt = os.path.join(entDir, entFile)
    destEnt = os.path.join(dp, entFile.replace('/', '-'))
    if os.path.isfile(srcEnt):
        shutil.copyfile(srcEnt, destEnt)
    else:
        shutil.copyfile(os.path.join(entDir, "empty.entities.yml"), destEnt)
