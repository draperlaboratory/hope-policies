# This silences python error trace backs, better for running tests set
# ERROR_MSGS to an empty string to print error trace backs
PYTHON ?= python3
ERROR_MSGS ?= --tb=long

TEST_FORMAT ?= junitxml
TEST_OUTPUT_FILE ?= report.xml

# default for unadorned `make`
CONFIG ?= qemu
all: build kernels run

# Standard build configurations can be listed here:
#   variable format: {config_name}_{VAR}
#   minimum variables (probably) needed: SIM, TESTS, RUNTIME, POLICIES

# simple qemu build
qemu_SIM = qemu
qemu_TESTS = hifive
qemu_RUNTIME = hifive
qemu_MODULE = osv.hifive.main
qemu_POLICIES = heap,none,rwx,stack,threeClass
qemu_XDIST = -n 25 # run in parallel
qemu: CONFIG=qemu
qemu: all

# simple renode build
renode_SIM = renode
renode_TESTS = frtos
renode_RUNTIME = frtos
renode_MODULE = osv.frtos.main
renode_POLICIES = heap,none,rwx,stack
renode_XDIST=
renode: CONFIG=renode
renode: all

# default test config settings that arn't commonly overwritten
COMPOSITE ?= simple
RULE_CACHE_SIZE ?= 16
DEBUG ?= no

PYTEST_ARGS ?= -v -rsxX --timeout=180 $(ERROR_MSGS) --sim=$(SIM) --isp_debug=$(DEBUG) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --policies=$(POLICIES) --composite=$(COMPOSITE) --module=$(MODULE)

# avoid short-circuiting targets based on local file/dir names
.PHONY: kernels

# build the tests 
build: SIM ?= $($(CONFIG)_SIM)
build: TESTS ?= $($(CONFIG)_TESTS)
build: RUNTIME ?= $($(CONFIG)_RUNTIME)
build: MODULE ?= $($(CONFIG)_MODULE)
build: POLICIES ?= $($(CONFIG)_POLICIES)
build: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build: 
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_build build_unit_tests.py

# build PEX kernels
kernels: SIM ?= $($(CONFIG)_SIM)
kernels: TESTS ?= $($(CONFIG)_TESTS)
kernels: RUNTIME ?= $($(CONFIG)_RUNTIME)
kernels: MODULE ?= $($(CONFIG)_MODULE)
kernels: POLICIES ?= $($(CONFIG)_POLICIES)
kernels: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
kernels:
	$(PYTHON) -m pytest $(PYTEST_ARGS) -k test_install_kernel install_kernels.py

# run tests
run: SIM ?= $($(CONFIG)_SIM)
run: TESTS ?= $($(CONFIG)_TESTS)
run: RUNTIME ?= $($(CONFIG)_RUNTIME)
run: MODULE ?= $($(CONFIG)_MODULE)
run: POLICIES ?= $($(CONFIG)_POLICIES)
run: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
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
