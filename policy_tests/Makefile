# This silences python error trace backs, better for running tests set
# ERROR_MSGS to an empty string to print error trace backs
PYTHON ?= python3
ERROR_MSGS ?= --tb=long

TEST_FORMAT ?= junitxml
TEST_OUTPUT_FILE ?= report.xml

# default test config settings that arn't commonly overwritten
COMPOSITE ?= simple
RULE_CACHE_SIZE ?= 16
DEBUG ?= no

# set args for config for targets called without any other specification
DEFAULT_SIM = qemu
DEFAULT_TESTS = hifive
DEFAULT_RUNTIME = hifive
DEFAULT_MODULE = osv.hifive.main
DEFAULT_POLICIES = heap,none,rwx,stack,threeClass
DEFAULT_XDIST = -n 1 # run in parallel

PYTEST_ARGS ?= -v -rsxX --timeout=180 $(ERROR_MSGS) --sim=$(SIM) --isp_debug=$(DEBUG) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --policies=$(POLICIES) --composite=$(COMPOSITE) --module=$(MODULE)

# TODO: find a way to report bad configs... maybe in pytest? ie no SIM set

# avoid short-circuiting targets based on local file/dir names
.PHONY: kernels

# QEMU build == defualt build
qemu: SIM ?= $(DEFAULT_SIM)
qemu: TESTS ?= $(DEFAULT_TESTS)
qemu: RUNTIME ?= $(DEFAULT_RUNTIME)
qemu: MODULE ?= $(DEFAULT_MODULE)
qemu: POLICIES ?= $(DEFAULT_POLICIES)
qemu: XDIST ?= $(DEFUALT_XDIST) # run in parallel
qemu: run

# Renode build defaults
renode: SIM ?= renode
renode: TESTS ?= frtos
renode: RUNTIME ?= frtos
renode: MODULE ?= osv.frtos.main
renode: POLICIES ?= heap,none,rwx,stack
renode: XDIST=
renode: run

# `make build` defaults to qemu config
build: SIM ?= $(DEFAULT_SIM)
build: TESTS ?= $(DEFAULT_TESTS)
build: RUNTIME ?= $(DEFAULT_RUNTIME)
build: MODULE ?= $(DEFAULT_MODULE)
build: POLICIES ?= $(DEFAULT_POLICIES)
build: XDIST ?= $(DEFUALT_XDIST) # run in parallel
build: 
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_build build_unit_tests.py

# `make kernels` defaults to qemu config
kernels: SIM ?= $(DEFAULT_SIM)
kernels: TESTS ?= $(DEFAULT_TESTS)
kernels: RUNTIME ?= $(DEFAULT_RUNTIME)
kernels: MODULE ?= $(DEFAULT_MODULE)
kernels: POLICIES ?= $(DEFAULT_POLICIES)
kernels: XDIST ?= $(DEFUALT_XDIST) # run in parallel
kernels:
	$(PYTHON) -m pytest $(PYTEST_ARGS) -k test_install_kernel install_kernels.py

# `make run` defualts to qemu config
run: SIM ?= $(DEFAULT_SIM)
run: TESTS ?= $(DEFAULT_TESTS)
run: RUNTIME ?= $(DEFAULT_RUNTIME)
run: MODULE ?= $(DEFAULT_MODULE)
run: POLICIES ?= $(DEFAULT_POLICIES)
run: XDIST ?= $(DEFUALT_XDIST) # run in parallel
run: build kernels
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_new run_unit_tests.py

list:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --collect-only run_unit_tests.py

list-kernels:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --collect-only install_kernels.py

list-build:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --collect-only build_unit_tests.py

clean: clean-kernels
	rm -rf output debug prof broken __pycache__ *.pyc assets report.html report.xml prof_results.log .cache

clean-kernels:
	rm -rf kernels/
