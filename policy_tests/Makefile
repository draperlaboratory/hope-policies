# This silences python error trace backs, better for running tests set
# ERROR_MSGS to an empty string to print error trace backs
PYTHON ?= python3
ERROR_MSGS ?= --tb=short

TEST_FORMAT ?= junitxml
TEST_OUTPUT_FILE ?= report.xml

# default for unadorned `make`
CONFIG ?= qemu
JOBS   ?= 1
all: build-tests build-kernels run-tests

# Standard build configurations can be listed here:
#   variable format: {config_name}_{VAR}
#   minimum variables (probably) needed: SIM, TESTS, RUNTIME, POLICIES

# simple qemu build
qemu_SIM = qemu
qemu_TESTS = hifive
qemu_RUNTIME = hifive
qemu_MODULE = osv.hifive.main
qemu_POLICIES = cfi,heap,rwx,stack,taint,threeClass,none,testSimple
qemu_POLICIES = cfi,heap,rwx,stack,threeClass,none,testSimple
qemu_XDIST = -n $(JOBS) # run in parallel
qemu: CONFIG=qemu
qemu: all

# simple renode build
renode_SIM = renode
renode_TESTS = frtos
renode_RUNTIME = frtos
renode_MODULE = osv.frtos.main
renode_POLICIES = cfi,heap,rwx,stack,taint,threeClass,none,testSimple
renode_XDIST=
renode: CONFIG=renode
renode: all

# default test config settings that arn't commonly overwritten
COMPOSITE ?= simple
RULE_CACHE_SIZE ?= 16
DEBUG ?= no

PYTEST_ARGS ?= --capture=no -v -rsx --timeout=180 $(ERROR_MSGS) --sim=$(SIM) --isp_debug=$(DEBUG) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --policies=$(POLICIES) --composite=$(COMPOSITE) --module=$(MODULE)

# RIPE Tests
build-ripe: SIM ?= $($(CONFIG)_SIM)
build-ripe: TESTS ?= $($(CONFIG)_TESTS)
build-ripe: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-ripe: MODULE ?= $($(CONFIG)_MODULE)
build-ripe: POLICIES ?= $($(CONFIG)_POLICIES)
build-ripe: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-ripe:
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_build_ripe ripe/ripe.py

run-ripe: SIM ?= $($(CONFIG)_SIM)
run-ripe: TESTS ?= $($(CONFIG)_TESTS)
run-ripe: RUNTIME ?= $($(CONFIG)_RUNTIME)
run-ripe: MODULE ?= $($(CONFIG)_MODULE)
run-ripe: POLICIES ?= $($(CONFIG)_POLICIES)
run-ripe: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
run-ripe: 
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_run_ripe ripe/ripe.py

ripe: build-kernels build-ripe run-ripe

# avoid short-circuiting targets based on local file/dir names
.PHONY: build-kernels

list: COLLECT_ONLY= --collect-only
list: run-tests

list-kernels: COLLECT_ONLY= --collect-only
list-kernels: build-kernels

list-build: COLLECT_ONLY= --collect-only
list-build: build-tests

install-runtime:
	isp_install_runtime frtos -b tests
	isp_install_runtime hifive -b tests

# build the tests 
build-tests: SIM ?= $($(CONFIG)_SIM)
build-tests: TESTS ?= $($(CONFIG)_TESTS)
build-tests: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-tests: MODULE ?= $($(CONFIG)_MODULE)
build-tests: POLICIES ?= $($(CONFIG)_POLICIES)
build-tests: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-tests: install-runtime 
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_build build_unit_tests.py

# build PEX kernels
build-kernels: SIM ?= $($(CONFIG)_SIM)
build-kernels: TESTS ?= $($(CONFIG)_TESTS)
build-kernels: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-kernels: MODULE ?= $($(CONFIG)_MODULE)
build-kernels: POLICIES ?= $($(CONFIG)_POLICIES)
build-kernels: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-kernels:
	$(PYTHON) -m pytest $(PYTEST_ARGS) $(COLLECT_ONLY) -k test_install_kernel install_kernels.py

# run tests
run-tests: SIM ?= $($(CONFIG)_SIM)
run-tests: TESTS ?= $($(CONFIG)_TESTS)
run-tests: RUNTIME ?= $($(CONFIG)_RUNTIME)
run-tests: MODULE ?= $($(CONFIG)_MODULE)
run-tests: POLICIES ?= $($(CONFIG)_POLICIES)
run-tests: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
run-tests: build-tests build-kernels
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_new run_unit_tests.py

clean: clean-kernels
	rm -rf output debug prof broken __pycache__ ripe/__pycache__ *.pyc assets report.html report.xml prof_results.log .cache \
		tests/isp-runtime-frtos* tests/isp-runtime-hifive* tests/*.o

clean-kernels:
	rm -rf kernels/
