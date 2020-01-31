# This silences python error trace backs, better for running tests set
# ERROR_MSGS to an empty string to print error trace backs
PYTHON ?= python3
ERROR_MSGS ?= --tb=short

TEST_FORMAT ?= junitxml
TEST_OUTPUT_FILE ?= report.xml

TEST_BUILD_DIR := build
TEST_OUTPUT_DIR := output

# default for unadorned `make`
CONFIG ?= bare-qemu
JOBS   ?= 1
all: build-dirs run-tests

# Arguments specific to running on an FPGA
BITSTREAM ?= $(ISP_PREFIX)/vcu118/bitstreams/soc_chisel_pipe_p1.bit
STOCK_BITSTREAM ?= $(ISP_PREFIX)/vcu118/bitstreams/soc_chisel_p1.bit

# Standard build configurations can be listed here:
#   variable format: {config_name}_{VAR}
#   minimum variables (probably) needed: SIM, TESTS, RUNTIME, GPOLICIES, POLICIES

# config for webapp tests and policies
webapp_SIM = qemu
webapp_TESTS = webapp
webapp_RUNTIME = bare
webapp_MODULE = osv.bare.main
webapp_GPOLICIES = 
webapp_POLICIES = none,userType,password,ppac,heap
webapp_XDIST = -n $(JOBS) # run in parallel
webapp_TIMEOUT = 360
webapp: CONFIG=webapp
webapp: all

# config for bare-metal on QEMU
bare-qemu_SIM = qemu
bare-qemu_TESTS = bare
bare-qemu_RUNTIME = bare
bare-qemu_MODULE = osv.bare.main
bare-qemu_GPOLICIES = 
bare-qemu_POLICIES = cfi,heap,rwx,stack,taint,threeClass,none,testSimple
bare-qemu_POLICIES = cfi,heap,rwx,stack,threeClass,none,testSimple
bare-qemu_XDIST = -n $(JOBS) # run in parallel
bare-qemu_TIMEOUT = 360
bare-qemu: CONFIG=bare-qemu
bare-qemu: all

# config for 64-bit bare-metal on QEMU
bare64-qemu_SIM = qemu
bare64-qemu_TESTS = bare64
bare64-qemu_RUNTIME = bare64
bare64-qemu_MODULE = osv.bare64.main
bare64-qemu_GPOLICIES = 
bare64-qemu_POLICIES = rwx,none
bare64-qemu_XDIST = -n $(JOBS) # run in parallel
bare64-qemu_TIMEOUT = 360
bare64-qemu_PYTEST_ARGS = --rv64
bare64-qemu: CONFIG=bare64-qemu
bare64-qemu: all

# config for bare-metal on VCU118 board
bare-vcu118_SIM = vcu118
bare-vcu118_TESTS = bare
bare-vcu118_RUNTIME = bare
bare-vcu118_MODULE = osv.bare.main
bare-vcu118_GPOLICIES = 
bare-vcu118_POLICIES = heap,stack,rwx
bare-vcu118_XDIST = -n $(JOBS) # run in parallel
bare-vcu118_TIMEOUT = 360
bare-vcu118_PYTEST_ARGS = --extra=+bitstream=$(BITSTREAM)
bare-vcu118: CONFIG=bare-vcu118
bare-vcu118: all

# config for bare-metal on VCU118 board without PIPE
bare-stock_SIM = vcu118
bare-stock_TESTS = bare
bare-stock_RUNTIME = bare
bare-stock_MODULE = osv.bare.main
bare-stock_GPOLICIES = 
bare-stock_POLICIES = none
bare-stock_XDIST = -n $(JOBS) # run in parallel
bare-stock_TIMEOUT = 360
bare-stock_PYTEST_ARGS = --extra=+bitstream=$(STOCK_BITSTREAM),+stock
bare-stock: CONFIG=bare-stock
bare-stock: all

# config for bare-metal in VCS sim
bare-vcs_SIM = vcs
bare-vcs_TESTS = bare
bare-vcs_RUNTIME = bare
bare-vcs_MODULE = osv.bare.main
bare-vcs_GPOLICIES = 
bare-vcs_POLICIES = rwx
bare-vcs_PYTEST_ARGS = --extra=+max-cycles=$(MAX_CYCLES),+pex-debug
bare-vcs_XDIST = -n $(JOBS) # run in parallel
bare-vcs_TIMEOUT = 0
bare-vcs: CONFIG=bare-vcs
bare-vcs: all

# config for FreeRTOS on QEMU
frtos-qemu_SIM = qemu
frtos-qemu_TESTS = frtos
frtos-qemu_RUNTIME = frtos
frtos-qemu_MODULE = osv.frtos.main
frtos-qemu_GPOLICIES = contextswitch
frtos-qemu_POLICIES = cfi,heap,rwx,stack,taint,threeClass,none,testSimple,testContext
frtos-qemu_XDIST= -n $(JOBS) # run in parallel
frtos-qemu_TIMEOUT = 360
frtos-qemu: CONFIG=frtos-qemu
frtos-qemu: all

# config for FreeRTOS on VCU118 board
frtos-vcu118_SIM = vcu118
frtos-vcu118_TESTS = frtos
frtos-vcu118_RUNTIME = frtos
frtos-vcu118_MODULE = osv.frtos.main
frtos-vcu118_GPOLICIES = contextswitch
frtos-vcu118_POLICIES = cfi,heap,rwx,stack,taint,threeClass,none,testSimple,testContext
frtos-vcu118_XDIST= -n $(JOBS) # run in parallel
frtos-vcu118_TIMEOUT = 360
frtos-vcu118_PYTEST_ARGS = --extra=+bitstream=$(BITSTREAM),+pex-debug
frtos-vcu118: CONFIG=frtos-vcu118
frtos-vcu118: all

# config for FreeRTOS in VCS sim
frtos-vcs_SIM = vcs
frtos-vcs_TESTS = frtos
frtos-vcs_RUNTIME = frtos
frtos-vcs_MODULE = osv.frtos.main
frtos-vcs_GPOLICIES =
frtos-vcs_POLICIES = rwx
frtos-vcs_XDIST= -n $(JOBS) # run in parallel
frtos-vcs_TIMEOUT = 0
frtos-vcs_PYTEST_ARGS = --extra=+pex-debug
frtos-vcs: CONFIG=frtos-vcs
frtos-vcs: all

# config for 64-bit FreeRTOS
frtos64-qemu_SIM = qemu
frtos64-qemu_TESTS = frtos64
frtos64-qemu_RUNTIME = frtos64
frtos64-qemu_MODULE = osv.frtos64.main
frtos64-qemu_GPOLICIES = contextswitch
frtos64-qemu_POLICIES = rwx,none,testContext
frtos64-qemu_XDIST= -n $(JOBS) # run in parallel
frtos64-qemu_TIMEOUT = 360
frtos64-qemu_PYTEST_ARGS = --rv64
frtos64-qemu: CONFIG=frtos64-qemu
frtos64-qemu: all

dhrystone_SIM = qemu
dhrystone_TESTS = dhrystone
dhrystone_RUNTIME = bare
dhrystone_MODULE = osv.bare.main
dhrystone_POLICIES = heap,rwx,stack,none,testSimple
dhrystone_XDIST = -n $(JOBS) # run in parallel
dhrystone_TIMEOUT = 360
dhrystone: CONFIG=dhrystone
dhrystone: all

# default test config settings that aren't commonly overwritten
COMPOSITE ?= simple
RULE_CACHE_SIZE ?= 16
DEBUG ?= no
MAX_CYCLES ?= 60000000

PYTEST_ARGS ?= --capture=no -v -rsx --timeout=$(TIMEOUT) --timeout-method=thread $(ERROR_MSGS) --sim=$(SIM) --isp_debug=$(DEBUG) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --gpolicies=$(GPOLICIES) --policies=$(POLICIES) --composite=$(COMPOSITE) --module=$(MODULE) --soc=$(SOC_CFG)

# RIPE Tests
RIPE_CONFIGS := ripe/ripe_configs.py
GEN_RIPE_CONFIGS := ripe/gen_ripe_configs.py

$(RIPE_CONFIGS): $(GEN_RIPE_CONFIGS)
	$(PYTHON) $(GEN_RIPE_CONFIGS) > $(RIPE_CONFIGS)

build-ripe: SIM ?= $($(CONFIG)_SIM)
build-ripe: TESTS ?= $($(CONFIG)_TESTS)
build-ripe: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-ripe: MODULE ?= $($(CONFIG)_MODULE)
build-ripe: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
build-ripe: POLICIES ?= $($(CONFIG)_POLICIES)
build-ripe: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-ripe: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
build-ripe: $(RIPE_CONFIGS)
	mkdir -p $(TEST_BUILD_DIR)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)/log
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_build_ripe ripe/ripe.py

run-ripe: SIM ?= $($(CONFIG)_SIM)
run-ripe: TESTS ?= $($(CONFIG)_TESTS)
run-ripe: RUNTIME ?= $($(CONFIG)_RUNTIME)
run-ripe: MODULE ?= $($(CONFIG)_MODULE)
run-ripe: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
run-ripe: POLICIES ?= $($(CONFIG)_POLICIES)
run-ripe: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
run-ripe: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
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
build-tests: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
build-tests: POLICIES ?= $($(CONFIG)_POLICIES)
build-tests: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-tests: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
build-tests: build-dirs
build-tests: build-kernels
	$(PYTHON) -m pytest $(PYTEST_ARGS) $($(CONFIG)_PYTEST_ARGS)  --$(TEST_FORMAT)=$(CONFIG)_build_$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_build build_unit_tests.py

build-dirs: SIM ?= $($(CONFIG)_SIM)
build-dirs: TESTS ?= $($(CONFIG)_TESTS)
build-dirs: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-dirs: MODULE ?= $($(CONFIG)_MODULE)
build-dirs: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
build-dirs: POLICIES ?= $($(CONFIG)_POLICIES)
build-dirs: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
build-dirs:
	mkdir -p $(TEST_BUILD_DIR)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)/$(SIM)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)/$(SIM)/log
	$(PYTHON) -m pytest $(PYTEST_ARGS) $($(CONFIG)_PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(COLLECT_ONLY) -k test_copy_build_dir build_unit_tests.py

tests: clean-tests build-tests

# PEX kernels
clean-kernels:
	rm -rf kernels/

build-kernels: SIM ?= $($(CONFIG)_SIM)
build-kernels: TESTS ?= $($(CONFIG)_TESTS)
build-kernels: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-kernels: MODULE ?= $($(CONFIG)_MODULE)
build-kernels: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
build-kernels: POLICIES ?= $($(CONFIG)_POLICIES)
build-kernels: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-kernels: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
build-kernels:
	$(PYTHON) -m pytest $(PYTEST_ARGS) $($(CONFIG)_PYTEST_ARGS) --$(TEST_FORMAT)=$(CONFIG)_policy_$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_install_kernel install_kernels.py

kernels: clean-kernels build-kernels

# run tests
run-tests: SIM ?= $($(CONFIG)_SIM)
run-tests: TESTS ?= $($(CONFIG)_TESTS)
run-tests: RUNTIME ?= $($(CONFIG)_RUNTIME)
run-tests: MODULE ?= $($(CONFIG)_MODULE)
run-tests: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
run-tests: POLICIES ?= $($(CONFIG)_POLICIES)
run-tests: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
run-tests: SOC_CFG ?= $($(CONFIG)_SOC_CFG)
run-tests: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
run-tests: build-tests
	mkdir -p $(TEST_OUTPUT_DIR)
	$(PYTHON) -m pytest $(PYTEST_ARGS) $($(CONFIG)_PYTEST_ARGS) --$(TEST_FORMAT)=$(CONFIG)_run_$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_new run_unit_tests.py

PERFORMANCE_REPORT_ARGS = -r $(RUNTIME) -s $(SIM) -p $(POLICIES) -t $(TESTS) -c $(if $(GPOLICIES),-g $(GPOLICIES),)

# generate performance report
performance-report: SIM ?= $($(CONFIG)_SIM)
performance-report: TESTS ?= performance
performance-report: RUNTIME ?= $($(CONFIG)_RUNTIME)
performance-report: MODULE ?= $($(CONFIG)_MODULE)
performance-report: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
performance-report: POLICIES ?= $($(CONFIG)_POLICIES)
performance-report: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
performance-report: SOC_CFG ?= $($(CONFIG)_SOC_CFG)
performance-report: TIMEOUT ?= 0
performance-report:
	TESTS=$(TESTS) TIMEOUT=$(TIMEOUT) $(MAKE) run-tests
	$(PYTHON) performance_report.py $(PERFORMANCE_REPORT_ARGS)

clean: clean-kernels clean-tests
	rm -rf $(TEST_BUILD_DIR) $(TEST_OUTPUT_DIR) $(RIPE_CONFIGS) debug prof broken __pycache__ ripe/__pycache__ *.pyc assets report.html *report.xml prof_results.log .cache \
		tests/isp-runtime-frtos* tests/isp-runtime-bare*
	find tests/ -type f -name '*.o' -delete
