import pytest
from setup_test import *
from cfg_classes import *

def pytest_addoption(parser):
    parser.addoption('--sim', default='renode',
                     help='Which sim to use (renode, qemu)')
    # TODO: add optimizations
    parser.addoption('--runtime', default='frtos',
                     help='What runtime should the test be compiled for')
    parser.addoption('--test', default='all',
                     help='Which test(s) to run')
    parser.addoption('--policies', default='simple',
                     help='Which policies to use, or simple, full, etc for combined policies')
    parser.addoption('--rule_cache', default='',
                     help='Which rule cache to use (ideal, finite, dmhc). Empty for none.')
    parser.addoption('--rule_cache_size', default=16, type=int,
                     help='size of rule cache, if one is used.')
    parser.addoption('--modules', default='osv.hifive.main',
                     help='which module(s) policies should be referenced from')
    parser.addoption('--composite', default='simple',
                     help='What composite policies (simple, full, else none)')
    
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

def pytest_generate_tests(metafunc):
    test_config = 'hifive' # TODO: remove
    #modules = configs[test_config].os_modules
    positive_tests = configs[test_config].positive_tests
    negative_tests = configs[test_config].negative_tests
#    policies = configs[test_config].policies

    modules = metafunc.config.option.modules.split(",")

    if 'policy' in metafunc.fixturenames:

        # gather passed policies
        policies = metafunc.config.option.policies.split(",")

        # build composites
        if 'simple' in metafunc.config.option.composite:
            policies = simpleK(modules, policies)
        elif 'full' in metafunc.config.option.composite:
            policies = fullK(modules, policies)

        # give all policies to test
        metafunc.parametrize("policy", policies, scope='session')
            
    if 'test' in metafunc.fixturenames:
        if 'all' in metafunc.config.option.test:
            all_tests = positive_tests + negative_tests
            metafunc.parametrize("test", all_tests,
                                 ids=list(map(fName, all_tests)),
                                 scope='session')
        else:
            tests = metafunc.config.option.test.split(",")
            metafunc.parametrize("test", tests,
                                 scope='session')
