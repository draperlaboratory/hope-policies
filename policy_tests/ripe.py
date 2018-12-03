import pytest
import errno
import os
import shutil

from helper_fns import *
from build_unit_tests import *
from run_unit_tests import *
#from ripe_config import *

def ripe_name(attack, tech, loc, ptr, func):
    return "ripe."+"-".join([attack,tech,loc,ptr,func])

@pytest.mark.parametrize("attack, tech, loc, ptr, func", [
    ("returnintolibc","direct","heap" ,"structfuncptrheap","memcpy"),
    ("rop"           ,"direct","stack","ret"              ,"memcpy"),
    ])
def test_build_ripe(attack, tech, loc, ptr, func, runtime):

    doMkDir("output/ripe")
    
    # "main" test name
    main = "ripe"

    # name for this test config
    name = test_name(ripe_name(attack, tech, loc, ptr, func), runtime)
    
    # this config dirpath 
    dirPath = t_directory(name)
    if os.path.isfile(os.path.join(dirPath, "build", "main")):
        pytest.skip("Test directory already exists: " + name)
    doMkDir(dirPath)

    # make policy-common test sources & tools
    doMkApp(runtime, dirPath, main)
    
    # make build dir for test
    doMkBuildDir(dirPath, runtime);

    # add ripe-specific Makefile
    mf_cflags = 'CFLAGS += '
    mf_cflags += '-DATTACK_TECHNIQUE=\\\"'+tech+'\\\" '
    mf_cflags += '-DATTACK_INJECT_PARAM=\\\"'+attack+'\\\" '
    mf_cflags += '-DATTACK_CODE_PTR=\\\"'+ptr+'\\\" '
    mf_cflags += '-DATTACK_LOCATION=\\\"'+loc+'\\\" '
    mf_cflags += '-DATTACK_FUNCTION=\\\"'+func+'\\\"'
    with open(os.path.join(dirPath, "srcs", "Makefile"), "w+") as f:
        f.write(mf_cflags)

    # do the build
    subprocess.Popen(["make"], stdout=open(os.path.join(dirPath, "build/build.log"), "w+"), stderr=subprocess.STDOUT, cwd=dirPath).wait()

    # check that build succeeded
    if not os.path.isfile(os.path.join(dirPath, "build", "main")):
        pytest.fail("No binary produced. Log: " + dirPath + "/build/build.log")

#@pytest.mark.parametrize("attack, tech, loc, ptr, func, policy", [
#    ("returnintolibc","direct","heap" ,"structfuncptrheap","memcpy", "osv.hifive.main.heap"),
#    ("returnintolibc","direct","heap" ,"structfuncptrheap","memcpy", "osv.hifive.main.heap-rwx-stack-threeClass"),
#    ("rop"           ,"direct","stack","ret"              ,"memcpy", "osv.hifive.main.stack"),
#    ("rop"           ,"direct","stack","ret"              ,"memcpy", "osv.hifive.main.heap-rwx-stack-threeClass")
#    ("rop"           ,"direct","stack","ret"              ,"memcpy", "osv.hifive.main.threeClass"),
#    ])
@pytest.mark.parametrize("attack, tech, loc, ptr, func, ripepols", [
    ("returnintolibc","direct","heap" ,"structfuncptrheap","memcpy", ["osv.hifive.main.heap", "osv.hifive.main.heap-rwx-stack-threeClass"]),
    ("rop"           ,"direct","stack","ret"              ,"memcpy", ["osv.hifive.main.stack", "osv.hifive.main.heap-rwx-stack-threeClass", "osv.hifive.main.threeClass"]),
    ])
def test_run_ripe(attack, tech, loc, ptr, func, ripepols, policy, runtime, sim, rc):

    config_name = ripe_name(attack, tech, loc, ptr, func)

    if policy not in ripepols:
        pytest.skip("Policy not expected to defeat attack")
    else:
        test_new(config_name, runtime, policy, sim, rc)
