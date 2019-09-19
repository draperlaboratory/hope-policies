import functools
import itertools
import operator
import pytest

from functools import reduce

from test_groups import *

def pytest_addoption(parser):
    parser.addoption('--sim', default='',
                     help='Which sim to use (renode, qemu)')
    # TODO: add optimizations
    parser.addoption('--runtime', default='',
                     help='What runtime should the test be compiled for')
    parser.addoption('--test', default='',
                     help='Which test(s) to run')
    parser.addoption('--gpolicies', default='',
                     help='Which global policies to use')
    parser.addoption('--policies', default='',
                     help='Which policies to use')
    parser.addoption('--rule_cache', default='',
                     help='Which rule cache to use (ideal, finite, dmhc). Empty for none.')
    parser.addoption('--rule_cache_size', default=16,
                     help='size of rule cache, if one is used.')
    parser.addoption('--module', default='',
                     help='optional policy prefix')
    parser.addoption('--composite', default='simple',
                     help='What composite policies (simple, full, else none)')
    parser.addoption('--isp_debug', default='no',
                     help='pass debug options to testing tasks (yes/no)')

@pytest.fixture
def sim(request):
    return request.config.getoption('--sim')

@pytest.fixture
def runtime(request):
    return request.config.getoption('--runtime')

@pytest.fixture
def rule_cache(request):
    return request.config.getoption('--rule_cache')

@pytest.fixture
def rule_cache_size(request):
    return request.config.getoption('--rule_cache_size')

@pytest.fixture
def composite(request):
    return request.config.getoption('--composite')

@pytest.fixture
def debug(request):
    return 'yes' == request.config.getoption('--isp_debug')

def pytest_generate_tests(metafunc):

    if 'policy' in metafunc.fixturenames:
        all_policies = []
        gpolicies = []
        policies = []

        # gather passed global policies
        gpolicies = list(filter(None, metafunc.config.option.gpolicies.split(",")))

        # gather passed policies
        policies = list(filter(None, metafunc.config.option.policies.split(",")))

        # build composites
        module = metafunc.config.option.module
        if module:
            if 'simple' in metafunc.config.option.composite:
                policies = composites(module, gpolicies, policies, True)
            elif 'full' in metafunc.config.option.composite:
                policies = composites(module, gpolicies, policies, False)
            else:
                policies = [module + "." + p for p in (gpolicies+policies)]
            
        # give all policies to test
        metafunc.parametrize("policy", policies, scope='session')

    if 'test' in metafunc.fixturenames:

        # "TESTS" as passed on the command line may be the names
        #   of individual tests, or the name of a group of tests
        #   defined in test_groups.py. The latter is the default
        #   in a case in which a group is given the same name as
        #   a test        
        test_arg = metafunc.config.option.test.split(",")

        # look up any test groups
        tests = []
        for t in test_arg:
            if t not in test_groups:
                tests.append(t)
            else:
                tests.extend(test_groups[t].tests)

        # unique (avoid duplicate work) & alphabetical (for XDIST)
        tests = sorted(list(set(tests))) 

        metafunc.parametrize("test", tests, scope='session')

    if 'rc' in metafunc.fixturenames:
        caches = metafunc.config.option.rule_cache.split(",")
        sizes  = metafunc.config.option.rule_cache_size.split(",")

        # combine rule cache options
        rcs = []
        for c in caches:
            for s in sizes:
                rcs.append((c, s))

        # with only 1 option, don't let rule-cache enter test name
        if len(rcs) == 1:
            rcs = [('','')]

        metafunc.parametrize("rc", rcs,
                             ids=list(map(lambda x: x[0]+x[1], rcs)),
                             scope='session')
        
# generate the permutations of policies to compose
def permutePols(polStrs):
    p = sorted(polStrs)
    # list of number of policies
    ns = list(range(1,len(p)+1))
    # list of combinations for each n
    combs = [list(map(sorted,itertools.combinations(p, n))) for n in ns]
    # flatten list
    return (reduce(operator.concat, combs, []))

# given modules and policies, generate composite policies
def composites(module, gpolicies, policies, simple):

    # generate all permutations
    r = []
    globalPols = permuteGlobalPols(gpolicies)
    localPols = permutePols(policies)
    if globalPols:
        localPols.append([])
    if localPols:
        globalPols.append([])

    for p in localPols:
        for gp in globalPols:
            if p or gp:
                r.append((p, module+"."+"-".join(gp+p)))

    # length of policy that has every member policy except none
    full_composite_len = len(policies)
    if "none" in policies:
        full_composite_len -= 1
    if "testSimple" in policies:
        full_composite_len -= 1
    if "testComplex" in policies:
        full_composite_len -= 1

    if simple: # single policies or full combination
        return [x[1] for x in r if len(x[0]) == 1 or
                (    (len(x[0]) == full_composite_len)
                 and (not "none" in x[0])
                 and (not "testSimple" in x[0])
                 and (not "testComplex" in x[0]))]
    else: # single policies or any combination without none
        return [x[1] for x in r if len(x[0]) == 1 or
                (     (not "none" in x[0])
                  and (not "testSimple" in x[0])
                  and (not "testComplex" in x[0]))]

# generate the permutations of policies to compose
def permuteGlobalPols(polStrs):
    p = (polStrs)
    # list of number of policies
    ns = list(range(1,len(p)+1))
    # list of combinations for each n
    combs = [list(map(sorted,itertools.combinations(p, n))) for n in ns]
    # flatten list
    return (reduce(operator.concat, combs, []))

