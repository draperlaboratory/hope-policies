import pytest
from setup_test import *
from cfg_classes import *


def pytest_addoption(parser):
    parser.addoption('--sim', default='renode',
                     help='Which sim to use (renode, qemu)')
    parser.addoption('--test_config', default='working',
                     help='Which test config to run from cfg_classes')
    parser.addoption('--remove_passing', default=False, action='store_true',
                     help='Delete passing test output directores')
    parser.addoption('--rule_cache', default='',
                     help='Which rule cache to use (ideal, finite, dmhc). Empty for none.')
    parser.addoption('--rule_cache_size', default=16, type=int,
                     help='Which rule cache to use (ideal, finite, dmhc). Empty for none.')

@pytest.fixture
def sim(request):
    return request.config.getoption('--sim')

@pytest.fixture
def test_config(request):
    return request.config.getoption('--test_config')

@pytest.fixture
def remove_passing(request):
    return request.config.getoption('--remove_passing')

@pytest.fixture
def rule_cache(request):
    return request.config.getoption('--rule_cache')

@pytest.fixture
def rule_cache_size(request):
    return request.config.getoption('--rule_cache_size')

def parameterize_test_file(varName, testFiles, metafunc):
    if varName in metafunc.fixturenames:
        metafunc.parametrize(varName, testFiles,
                             ids=list(map(fName, testFiles)),
                             scope='session')


def pytest_generate_tests(metafunc):
    test_config = metafunc.config.option.test_config
    modules = configs[test_config].os_modules
    positive_tests = configs[test_config].positive_tests
    negative_tests = configs[test_config].negative_tests
    policies = configs[test_config].policies
    broken_tests = []
    profile_tests = []

    if 'simplePol' in metafunc.fixturenames:
        simplePols = simpleK(modules, policies)
        metafunc.parametrize("simplePol", simplePols,
                             ids=list(map(trd, simplePols)),
                             scope='session')
    if 'fullPol' in metafunc.fixturenames:
        fullPols = fullK(modules, policies)
        metafunc.parametrize("fullPol", fullPols,
                             ids=list(map(trd, fullPols)),
                             scope='session')

    parameterize_test_file("testFile", positive_tests+negative_tests, metafunc)
    parameterize_test_file("brokenTestFile", broken_tests, metafunc)
    parameterize_test_file("profileTestFile", profile_tests, metafunc)
