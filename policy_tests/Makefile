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
BITSTREAM ?= soc_chisel_pipe_p1
AP_TTY ?= /dev/ttyUSB1
PEX_TTY ?= /dev/ttyUSB0

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
bare-qemu_SOC_CFG = $(ISP_PREFIX)/sources/policy-engine/soc_cfg/hifive_e_cfg.yml
bare-qemu: CONFIG=bare-qemu
bare-qemu: all

# config for bare-metal on VCU118 board
bare-vcu118_SIM = vcu118
bare-vcu118_TESTS = bare
bare-vcu118_RUNTIME = bare
bare-vcu118_MODULE = osv.bare.main
bare-vcu118_GPOLICIES = 
bare-vcu118_POLICIES = rwx
bare-vcu118_XDIST = -n $(JOBS) # run in parallel
bare-vcu118_SOC_CFG = $(ISP_PREFIX)/sources/policy-engine/soc_cfg/gfe-vcu118.yml
bare-vcu118_PYTEST_ARGS = --extra=+program,+bitstream=$(BITSTREAM),+ap-tty=$(AP_TTY),+pex-tty=$(PEX_TTY)
bare-vcu118: CONFIG=bare-vcu118
bare-vcu118: all

# config for FreeRTOS
frtos_SIM = qemu
frtos_TESTS = frtos
frtos_RUNTIME = frtos
frtos_MODULE = osv.frtos.main
frtos_GPOLICIES = contextswitch
frtos_POLICIES = cfi,heap,rwx,stack,taint,threeClass,none,testSimple,testContext
frtos_XDIST= -n $(JOBS) # run in parallel
frtos: CONFIG=frtos
frtos: all

dhrystone_SIM = qemu
dhrystone_TESTS = dhrystone
dhrystone_RUNTIME = bare
dhrystone_MODULE = osv.bare.main
dhrystone_POLICIES = heap,rwx,stack,none,testSimple
dhrystone_XDIST = -n $(JOBS) # run in parallel
dhrystone: CONFIG=dhrystone
dhrystone: all

# default test config settings that arn't commonly overwritten
COMPOSITE ?= simple
RULE_CACHE_SIZE ?= 16
DEBUG ?= no

PYTEST_ARGS ?= --capture=no -v -rsx --timeout=360 --timeout-method=thread $(ERROR_MSGS) --sim=$(SIM) --isp_debug=$(DEBUG) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --gpolicies=$(GPOLICIES) --policies=$(POLICIES) --composite=$(COMPOSITE) --module=$(MODULE) --soc=$(SOC_CFG)

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
build-tests: build-dirs
build-tests: build-kernels
	$(PYTHON) -m pytest $(PYTEST_ARGS) $($(CONFIG)_PYTEST_ARGS)  --$(TEST_FORMAT)=$(CONFIG)_build_$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_build build_unit_tests.py

build-dirs: SIM ?= $($(CONFIG)_SIM)
build-dirs: TESTS ?= $($(CONFIG)_TESTS)
build-dirs: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-dirs: MODULE ?= $($(CONFIG)_MODULE)
build-dirs: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
build-dirs: POLICIES ?= $($(CONFIG)_POLICIES)
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
run-tests: build-tests
	mkdir -p $(TEST_OUTPUT_DIR)
	$(PYTHON) -m pytest $(PYTEST_ARGS) $($(CONFIG)_PYTEST_ARGS) --$(TEST_FORMAT)=$(CONFIG)_run_$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_new run_unit_tests.py

clean: clean-kernels clean-tests
	rm -rf $(TEST_BUILD_DIR) $(TEST_OUTPUT_DIR) $(RIPE_CONFIGS) debug prof broken __pycache__ ripe/__pycache__ *.pyc assets report.html *report.xml prof_results.log .cache \
		tests/isp-runtime-frtos* tests/isp-runtime-bare*
	find tests/ -type f -name '*.o' -delete
