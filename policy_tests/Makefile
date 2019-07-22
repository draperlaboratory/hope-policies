# This silences python error trace backs, better for running tests set
# ERROR_MSGS to an empty string to print error trace backs
PYTHON ?= python3
ERROR_MSGS ?= --tb=short

TEST_FORMAT ?= junitxml
TEST_OUTPUT_FILE ?= report.xml

TEST_BUILD_DIR := build
TEST_OUTPUT_DIR := output

# default for unadorned `make`
CONFIG ?= bare
JOBS   ?= 1
all: build-tests build-kernels run-tests
stock_all: run-tests-stock

# Standard build configurations can be listed here:
#   variable format: {config_name}_{VAR}
#   minimum variables (probably) needed: SIM, TESTS, RUNTIME, POLICIES

# config for webapp tests and policies
webapp_SIM = qemu
webapp_TESTS = webapp
webapp_RUNTIME = bare
webapp_MODULE = osv.bare.main
webapp_POLICIES = none,userType,password,ppac,heap
webapp_XDIST = -n $(JOBS) # run in parallel
webapp: CONFIG=webapp
webapp: all

# config for bare-metal
bare_SIM = qemu
bare_TESTS = bare
bare_RUNTIME = bare
bare_MODULE = osv.bare.main
bare_POLICIES = cfi,heap,rwx,stack,taint,threeClass,none,testSimple
bare_POLICIES = cfi,heap,rwx,stack,threeClass,none,testSimple
bare_XDIST = -n $(JOBS) # run in parallel
bare: CONFIG=bare
bare: all

# config for FreeRTOS
frtos_SIM = qemu
frtos_TESTS = frtos
frtos_RUNTIME = frtos
frtos_MODULE = osv.frtos.main
frtos_POLICIES = cfi,heap,rwx,stack,taint,threeClass,none,testSimple
frtos_XDIST= -n $(JOBS) # run in parallel
frtos: CONFIG=frtos
frtos: all

# config for stock bare-metal
stock_bare_SIM = qemu_stock
stock_bare_TESTS = stock_bare
stock_bare_RUNTIME = stock_bare
stock_bare_MODULE = osv.stock_bare.main
stock_bare_POLICIES = none
stock_bare_XDIST = -n $(JOBS) # run in parallel
stock_bare: CONFIG=stock_bare
stock_bare: stock_all

# config for Stock FreeRTOS
stock_frtos_SIM = qemu_stock
stock_frtos_TESTS = stock_frtos
stock_frtos_RUNTIME = stock_frtos
stock_frtos_MODULE = osv.stock_frtos.main
stock_frtos_POLICIES = none
stock_frtos_XDIST= -n $(JOBS) # run in parallel
stock_frtos: CONFIG=stock_frtos
stock_frtos: stock_all

dhrystone_SIM = qemu
dhrystone_TESTS = dhrystone
dhrystone_RUNTIME = bare
dhrystone_MODULE = osv.bare.main
dhrystone_POLICIES = heap,rwx,stack,none,testSimple
dhrystone_XDIST = -n $(JOBS) # run in parallel
dhrystone: CONFIG=dhrystone
dhrystone: all

# config for Rhealstone
rhealstone_SIM = qemu
rhealstone_TESTS = rhealstone_group
rhealstone_RUNTIME = frtos
rhealstone_MODULE = osv.$(rhealstone_RUNTIME).main
rhealstone_POLICIES = none,stack,heap,rwx,cfi
rhealstone_XDIST = -n $(JOBS) # run in parallel
rhealstone: CONFIG=rhealstone
rhealstone: all report-rhealstone
rhealstone-build: CONFIG=rhealstone
rhealstone-build: build-tests

# config for Rhealstone
rhealstone-stock_SIM = qemu_stock
rhealstone-stock_TESTS = rhealstone_group
rhealstone-stock_RUNTIME = stock_frtos
rhealstone-stock_MODULE = osv.$(rhealstone-stock_RUNTIME).main
rhealstone-stock_POLICIES = none
rhealstone-stock_XDIST = -n $(JOBS) # run in parallel
rhealstone-stock: CONFIG=rhealstone-stock
rhealstone-stock: rhealstone-stock-build
rhealstone-stock-build: CONFIG=rhealstone-stock
rhealstone-stock-build: build-tests-stock

# default test config settings that arn't commonly overwritten
COMPOSITE ?= simple
RULE_CACHE_SIZE ?= 16
DEBUG ?= no

PYTEST_ARGS ?= --capture=no -v -rsx --timeout=360 --timeout-method=thread $(ERROR_MSGS) --sim=$(SIM) --isp_debug=$(DEBUG) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --policies=$(POLICIES) --composite=$(COMPOSITE) --module=$(MODULE)

# RIPE Tests
RIPE_CONFIGS := ripe/ripe_configs.py
GEN_RIPE_CONFIGS := ripe/gen_ripe_configs.py

$(RIPE_CONFIGS): $(GEN_RIPE_CONFIGS)
	$(PYTHON) $(GEN_RIPE_CONFIGS) > $(RIPE_CONFIGS)

build-ripe: SIM ?= $($(CONFIG)_SIM)
build-ripe: TESTS ?= $($(CONFIG)_TESTS)
build-ripe: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-ripe: MODULE ?= $($(CONFIG)_MODULE)
build-ripe: POLICIES ?= $($(CONFIG)_POLICIES)
build-ripe: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-ripe: $(RIPE_CONFIGS)
	mkdir -p $(TEST_BUILD_DIR)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)/log
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_build_ripe ripe/ripe.py

run-ripe: SIM ?= $($(CONFIG)_SIM)
run-ripe: TESTS ?= $($(CONFIG)_TESTS)
run-ripe: RUNTIME ?= $($(CONFIG)_RUNTIME)
run-ripe: MODULE ?= $($(CONFIG)_MODULE)
run-ripe: POLICIES ?= $($(CONFIG)_POLICIES)
run-ripe: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
run-ripe:
	mkdir -p $(TEST_OUTPUT_DIR)
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

# Tests
clean-tests:
	rm -rf build/

build-tests: SIM ?= $($(CONFIG)_SIM)
build-tests: TESTS ?= $($(CONFIG)_TESTS)
build-tests: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-tests: MODULE ?= $($(CONFIG)_MODULE)
build-tests: POLICIES ?= $($(CONFIG)_POLICIES)
build-tests: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-tests: build-dirs
build-tests: build-kernels
	mkdir -p $(TEST_BUILD_DIR)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)/log
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_build build_unit_tests.py

build-tests-stock: SIM ?= $($(CONFIG)_SIM)
build-tests-stock: TESTS ?= $($(CONFIG)_TESTS)
build-tests-stock: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-tests-stock: MODULE ?= $($(CONFIG)_MODULE)
build-tests-stock: POLICIES ?= $($(CONFIG)_POLICIES)
build-tests-stock: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-tests-stock: build-dirs
	mkdir -p $(TEST_BUILD_DIR)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)/log
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_build build_unit_tests.py

build-dirs: SIM ?= $($(CONFIG)_SIM)
build-dirs: TESTS ?= $($(CONFIG)_TESTS)
build-dirs: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-dirs: MODULE ?= $($(CONFIG)_MODULE)
build-dirs: POLICIES ?= $($(CONFIG)_POLICIES)
build-dirs:
	mkdir -p $(TEST_BUILD_DIR)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)/log
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(COLLECT_ONLY) -k test_copy_build_dir build_unit_tests.py

tests: clean-tests build-tests

# PEX kernels
clean-kernels:
	rm -rf kernels/

build-kernels: SIM ?= $($(CONFIG)_SIM)
build-kernels: TESTS ?= $($(CONFIG)_TESTS)
build-kernels: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-kernels: MODULE ?= $($(CONFIG)_MODULE)
build-kernels: POLICIES ?= $($(CONFIG)_POLICIES)
build-kernels: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-kernels:
	$(PYTHON) -m pytest $(PYTEST_ARGS) $(XDIST) $(COLLECT_ONLY) -k test_install_kernel install_kernels.py

kernels: clean-kernels build-kernels

# run tests
run-tests: SIM ?= $($(CONFIG)_SIM)
run-tests: TESTS ?= $($(CONFIG)_TESTS)
run-tests: RUNTIME ?= $($(CONFIG)_RUNTIME)
run-tests: MODULE ?= $($(CONFIG)_MODULE)
run-tests: POLICIES ?= $($(CONFIG)_POLICIES)
run-tests: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
run-tests: build-tests
	mkdir -p $(TEST_OUTPUT_DIR)
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_new run_unit_tests.py

run-tests-stock: SIM ?= $($(CONFIG)_SIM)
run-tests-stock: TESTS ?= $($(CONFIG)_TESTS)
run-tests-stock: RUNTIME ?= $($(CONFIG)_RUNTIME)
run-tests-stock: MODULE ?= $($(CONFIG)_MODULE)
run-tests-stock: POLICIES ?= $($(CONFIG)_POLICIES)
run-tests-stock: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
run-tests-stock: build-tests-stock
	mkdir -p $(TEST_OUTPUT_DIR)
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_new run_unit_tests.py

clean: clean-kernels clean-tests
	rm -rf $(TEST_BUILD_DIR) $(TEST_OUTPUT_DIR) $(RIPE_CONFIGS) debug prof broken __pycache__ ripe/__pycache__ *.pyc assets report.html report.xml prof_results.log .cache \
		tests/isp-runtime-frtos* tests/isp-runtime-bare*
	find tests/ -type f -name '*.o' -delete

report-rhealstone:
	python3 tests/rhealstone/report_rhealstone.py --policies "$(rhealstone_POLICIES)"
