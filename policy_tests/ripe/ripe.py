import pytest
import errno
import os
import shutil

from ripe_configs import *
from policy_tests_utils import *

import policy_tests_run
import isp_build

def ripe_name(attack, tech, loc, ptr, func):
    return "ripe."+"-".join([attack,tech,loc,ptr,func])

@pytest.mark.parametrize("attack, tech, loc, ptr, func", [(c[0], c[1], c[2], c[3], c[4]) for c in RipeConfigs.configs])
def test_build_ripe(attack, tech, loc, ptr, func, runtime):

    if not runtime:
        pytest.fail("No target runtime provided")

    name = policy_test_name(ripe_name(attack, tech, loc, ptr, func), runtime)
    out_dir = policy_test_directory(name)
    if os.path.isfile(os.path.join(out_dir, "build", "main")):
        pytest.skip("Test directory already exists: " + name)
    doMkDir(out_dir)

    src_dir = os.path.join(out_dir, "srcs")
    doMkDir(src_dir)
    
    test_path = os.path.join("tests", "ripe")
    if os.path.isfile(test_path):
        shutil.copy(test_path, src_dir)
    elif os.path.isdir(test_path):
        for f in os.listdir(test_path):
            shutil.copy(os.path.join(test_path, f), src_dir)
    else:
        pytest.skip("No test found")

    # generic test code 
    shutil.copy(os.path.join("template", "test.h"), src_dir)
    shutil.copy(os.path.join("template", "test_status.c"), src_dir)
    shutil.copy(os.path.join("template", "test_status.h"), src_dir)
    shutil.copy(os.path.join("template", "sifive_test.h"), src_dir)

    # add ripe-specific Makefile
    mf_cflags = 'CFLAGS += '
    mf_cflags += '-DATTACK_TECHNIQUE=\\\"'+tech+'\\\" '
    mf_cflags += '-DATTACK_INJECT_PARAM=\\\"'+attack+'\\\" '
    mf_cflags += '-DATTACK_CODE_PTR=\\\"'+ptr+'\\\" '
    mf_cflags += '-DATTACK_LOCATION=\\\"'+loc+'\\\" '
    mf_cflags += '-DATTACK_FUNCTION=\\\"'+func+'\\\"'
    with open(os.path.join(src_dir, "Makefile"), "w+") as f:
        f.write(mf_cflags)

    # create entity for file elements
    entDir = os.path.abspath("../entities")
    entFile = "ripe" + ".entities.yml"
    srcEnt = os.path.join(entDir, entFile)
    destEnt = os.path.join(out_dir, entFile.replace('/', '-'))
    if os.path.isfile(srcEnt):
        shutil.copyfile(srcEnt, destEnt)
    else:
        shutil.copyfile(os.path.join(entDir, "empty.entities.yml"), destEnt)
    
    # do the build
    res = isp_build.do_build(src_dir, "template", runtime, out_dir, copy_src = False)

    if res != isp_build.retVals.SUCCESS:
        pytest.fail(res)


@pytest.mark.parametrize("attack, tech, loc, ptr, func, ripepols", RipeConfigs.configs, ids = ["-".join([c[0], c[1], c[2], c[3], c[4]]) for c in RipeConfigs.configs])
def test_run_ripe(attack, tech, loc, ptr, func, ripepols, policy, runtime, sim, rc):

    config_name = ripe_name(attack, tech, loc, ptr, func)

    if policy not in ripepols:
        pytest.skip("Policy not expected to defeat attack")
    else:
        policy_tests_run.test_run(config_name, runtime, policy, sim, rc)
