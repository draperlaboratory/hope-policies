import pytest
import errno
import os
import shutil
import helper_fns
import build_unit_tests
import run_unit_tests
import ripe_configs

def ripeName(attack, tech, loc, ptr, func):
    return os.path.join("ripe", "-".join(["ripe", tech,attack,ptr,loc,func]))

configs = ripe_configs.RipeConfigs.configs

@pytest.mark.parametrize("attack, tech, loc, ptr, func",
                         [tuple(c[:5]) for c in configs])
def test_build_ripe(attack, tech, loc, ptr, func, runtime):
    extra_env = {"INJECT_PARAM" : attack,
                 "TECHNIQUE" : tech,
                 "LOCATION" : loc,
                 "CODE_PTR" : ptr,
                 "FUNCTION" : func}

    test = ripeName(attack, tech, loc, ptr, func)
    build_unit_tests.test_build(test, runtime, extra_env=extra_env)


@pytest.mark.parametrize("attack, tech, loc, ptr, func, ripepols",
                         configs,
                         ids = ["-".join(c[:5]) for c in configs])
def test_run_ripe(attack, tech, loc, ptr, func, ripepols, policy, runtime, sim, rule_cache):
    test = ripeName(attack, tech, loc, ptr, func)
    
    if policy not in ripepols:
        pytest.skip("Policy not expected to defeat attack")
    else:
        run_unit_tests.test_new(test, runtime, policy, sim, rule_cache, "ripe")
