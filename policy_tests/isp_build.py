import functools
import itertools
import operator
import subprocess
import os
import shutil
import time
import glob
import errno

from isp_utils import *

class retVals:
    UNKNOWN_FAIL = "No binary produced"
    NO_RUNTIME   = "Target runtime not found"
    NO_TEST      = "Target source not found"
    SUCCESS      = "Target built successfully"

def do_build(src_dir,
             runtime,
             out_dir,
             copy_src = True):

    if not os.path.isdir(src_dir):
        return retVals.NO_TEST
    
    # output directory
    doMkDir(out_dir)
    
    if copy_src:
        src_copy = os.path.join(out_dir, "srcs")
        doMkDir(src_copy)
        for f in os.listdir(src_dir):
            shutil.copy(os.path.join(src_dir, f), src_copy)
        src_dir = src_copy

    # make policy-common test sources & tools
    add_runtime(runtime, out_dir, src_dir)
    
    # make build dir for test
    make_build_dir(out_dir, runtime);
        
    # do the build
    subprocess.Popen(["make"], stdout=open(os.path.join(out_dir, "build/build.log"), "w+"), stderr=subprocess.STDOUT, cwd=out_dir).wait()

    # check that build succeeded
    if not os.path.isfile(os.path.join(out_dir, "build", "main")):
        return retVals.UNKNOWN_FAIL

    return retVals.SUCCESS
    
def make_build_dir(dp, runtime):

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
        
def add_runtime(runtime, dp, src_dir):

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
        return isp.buildRetVals.NO_RUNTIME
