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
webapp_MODULE = osv
webapp_ARCH = rv32
webapp_GPOLICIES = 
webapp_POLICIES = none,userType,password,ppac,heap
webapp_XDIST = -n $(JOBS) # run in parallel
webapp_TIMEOUT = 360
webapp: CONFIG=webapp
webapp: all

# config for 32-bit hifive bare-metal on QEMU
bare-hifive32_SIM = qemu
bare-hifive32_TESTS = bare
bare-hifive32_RUNTIME = bare
bare-hifive32_ARCH = rv32
bare-hifive32_MODULE = osv
bare-hifive32_GPOLICIES = 
bare-hifive32_POLICIES = rwx,none,heap,taint,testSimple
bare-hifive32_XDIST = -n $(JOBS) # run in parallel
bare-hifive32_TIMEOUT = 360
bare-hifive32_SOC_CFG = hifive32
bare-hifive32: CONFIG=bare-hifive32
bare-hifive32: all

# config for 32-bit hifive FreeRTOS on QEMU
frtos-hifive32_SIM = qemu
frtos-hifive32_TESTS = frtos
frtos-hifive32_RUNTIME = frtos
frtos-hifive32_ARCH = rv32
frtos-hifive32_MODULE = osv.frtos.main
frtos-hifive32_GPOLICIES = contextswitch
frtos-hifive32_POLICIES = rwx,none,testContext,heap,taint,testSimple
frtos-hifive32_XDIST= -n $(JOBS) # run in parallel
frtos-hifive32_TIMEOUT = 360
frtos-hifive32_SOC_CFG = hifive32
frtos-hifive32: CONFIG=frtos-hifive32
frtos-hifive32: all

# config for 64-bit hifive bare-metal on QEMU
bare-hifive64_SIM = qemu
bare-hifive64_TESTS = bare64
bare-hifive64_RUNTIME = bare
bare-hifive64_ARCH = rv64
bare-hifive64_MODULE = osv
bare-hifive64_GPOLICIES = 
bare-hifive64_POLICIES = rwx,none,heap,taint,testSimple
bare-hifive64_XDIST = -n $(JOBS) # run in parallel
bare-hifive64_TIMEOUT = 360
bare-hifive64_SOC_CFG = hifive64
bare-hifive64: CONFIG=bare-hifive64
bare-hifive64: all

# config for 64-bit hifive FreeRTOS on QEMU
frtos-hifive64_SIM = qemu
frtos-hifive64_TESTS = frtos64
frtos-hifive64_RUNTIME = frtos
frtos-hifive64_ARCH = rv64
frtos-hifive64_MODULE = osv.frtos.main
frtos-hifive64_GPOLICIES = contextswitch
frtos-hifive64_POLICIES = rwx,none,testContext,heap,taint,testSimple
frtos-hifive64_XDIST= -n $(JOBS) # run in parallel
frtos-hifive64_TIMEOUT = 360
frtos-hifive64_SOC_CFG = hifive64
frtos-hifive64: CONFIG=frtos-hifive64
frtos-hifive64: all

# config for SSITH P1 bare-metal on VCU118 board
bare-ssith-p1_SIM = vcu118
bare-ssith-p1_TESTS = bare
bare-ssith-p1_RUNTIME = bare
bare-ssith-p1_ARCH = rv32
bare-ssith-p1_MODULE = osv
bare-ssith-p1_GPOLICIES = 
bare-ssith-p1_POLICIES = heap,rwx
bare-ssith-p1_XDIST = -n $(JOBS) # run in parallel
bare-ssith-p1_TIMEOUT = 360
bare-ssith-p1_SOC_CFG = ssith-p1
bare-ssith-p1_PYTEST_ARGS = --extra=+bitstream=$(BITSTREAM)
bare-ssith-p1: CONFIG=bare-ssith-p1
bare-ssith-p1: all

# config for SSITH P1 FRTOS on VCU118 board
frtos-ssith-p1_SIM = vcu118
frtos-ssith-p1_TESTS = frtos
frtos-ssith-p1_RUNTIME = frtos
frtos-ssith-p1_ARCH = rv32
frtos-ssith-p1_MODULE = osv
frtos-ssith-p1_GPOLICIES = 
frtos-ssith-p1_POLICIES = heap,rwx
frtos-ssith-p1_XDIST = -n $(JOBS) # run in parallel
frtos-ssith-p1_TIMEOUT = 360
frtos-ssith-p1_SOC_CFG = ssith-p1
frtos-ssith-p1_PYTEST_ARGS = --extra=+bitstream=$(BITSTREAM)
frtos-ssith-p1: CONFIG=frtos-ssith-p1
frtos-ssith-p1: all

# config for SSITH P2 bare-metal on VCU118 board
bare-ssith-p2_SIM = vcu118
bare-ssith-p2_TESTS = bare64
bare-ssith-p2_RUNTIME = bare
bare-ssith-p2_ARCH = rv64
bare-ssith-p2_MODULE = osv
bare-ssith-p2_GPOLICIES = 
bare-ssith-p2_POLICIES = heap,rwx
bare-ssith-p2_XDIST = -n $(JOBS) # run in parallel
bare-ssith-p2_TIMEOUT = 360
bare-ssith-p2_SOC_CFG = ssith-p2
bare-ssith-p2_PYTEST_ARGS = --extra=+bitstream=$(BITSTREAM)
bare-ssith-p2: CONFIG=bare-ssith-p2
bare-ssith-p2: all

# config for SSITH P2 FRTOS on VCU118 board
frtos-ssith-p2_SIM = vcu118
frtos-ssith-p2_TESTS = frtos64
frtos-ssith-p2_RUNTIME = frtos
frtos-ssith-p2_ARCH = rv64
frtos-ssith-p2_MODULE = osv
frtos-ssith-p2_GPOLICIES = 
frtos-ssith-p2_POLICIES = heap,rwx
frtos-ssith-p2_XDIST = -n $(JOBS) # run in parallel
frtos-ssith-p2_TIMEOUT = 360
frtos-ssith-p2_SOC_CFG = ssith-p2
frtos-ssith-p2_PYTEST_ARGS = --extra=+bitstream=$(BITSTREAM)
frtos-ssith-p2: CONFIG=frtos-ssith-p2
frtos-ssith-p2: all

# config for 64-bit bare-metal on Iveia board
bare-iveia_SIM = iveia
bare-iveia_TESTS = hello_works_1
bare-iveia_RUNTIME = bare
bare-iveia_ARCH = rv64
bare-iveia_MODULE = osv
bare-iveia_GPOLICIES =
bare-iveia_POLICIES = rwx
bare-iveia_XDIST = -n $(JOBS) # run in parallel
bare-iveia_TIMEOUT = 360
bare-iveia_SOC_CFG = iveia
bare-iveia_PYTEST_ARGS = --extra=+ap-address="0x78040000",+kernel-address="0x40000000",+pex-br="57600"
bare-iveia: CONFIG=bare-iveia
bare-iveia: all

# config for bare-metal on VCU118 board without PIPE
bare-stock_SIM = vcu118
bare-stock_TESTS = bare
bare-stock_RUNTIME = bare
bare-stock_MODULE = osv
bare-stock_ARCH = rv32
bare-stock_GPOLICIES = 
bare-stock_POLICIES = none
bare-stock_XDIST = -n $(JOBS) # run in parallel
bare-stock_TIMEOUT = 360
bare-stock_SOC_CFG = vcu118
bare-stock_PYTEST_ARGS = --extra=+bitstream=$(STOCK_BITSTREAM),+stock
bare-stock: CONFIG=bare-stock
bare-stock: all

dhrystone_SIM = qemu
dhrystone_TESTS = dhrystone
dhrystone_RUNTIME = bare
dhrystone_MODULE = osv
dhrystone_ARCH = rv32
dhrystone_POLICIES = heap,rwx,stack,none,testSimple
dhrystone_XDIST = -n $(JOBS) # run in parallel
dhrystone_TIMEOUT = 360
dhrystone_SOC_CFG = hifive
dhrystone: CONFIG=dhrystone
dhrystone: all

# default test config settings that aren't commonly overwritten
COMPOSITE ?= simple
RULE_CACHE_SIZE ?= 16
_DEBUG ?= no-debug
MAX_CYCLES ?= 60000000

ifdef DEBUG
_DEBUG = debug
endif

PYTEST_ARGS ?= --capture=no -v -rsx --timeout=$(TIMEOUT) --timeout-method=thread $(ERROR_MSGS) --sim=$(SIM) --isp_debug=$(_DEBUG) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --arch=$(ARCH) --gpolicies=$(GPOLICIES) --policies=$(POLICIES) --composite=$(COMPOSITE) --module=$(MODULE) --soc=$($(CONFIG)_SOC_CFG)

# RIPE Tests
RIPE_CONFIGS := ripe/ripe_configs.py
GEN_RIPE_CONFIGS := ripe/gen_ripe_configs.py

$(RIPE_CONFIGS): $(GEN_RIPE_CONFIGS)
	$(PYTHON) $(GEN_RIPE_CONFIGS) > $(RIPE_CONFIGS)

build-ripe: SIM ?= $($(CONFIG)_SIM)
build-ripe: TESTS ?= $($(CONFIG)_TESTS)
build-ripe: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-ripe: ARCH ?= $($(CONFIG)_ARCH)
build-ripe: MODULE ?= $($(CONFIG)_MODULE)
build-ripe: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
build-ripe: POLICIES ?= $($(CONFIG)_POLICIES)
build-ripe: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-ripe: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
build-ripe: $(RIPE_CONFIGS)
	mkdir -p $(TEST_BUILD_DIR)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)/$(ARCH)
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)/$(ARCH)/log
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(_DEBUG)_$(TEST_OUTPUT_FILE) $(XDIST) -k test_build_ripe ripe/ripe.py

run-ripe: SIM ?= $($(CONFIG)_SIM)
run-ripe: TESTS ?= $($(CONFIG)_TESTS)
run-ripe: RUNTIME ?= $($(CONFIG)_RUNTIME)
run-ripe: ARCH ?= $($(CONFIG)_ARCH)
run-ripe: MODULE ?= $($(CONFIG)_MODULE)
run-ripe: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
run-ripe: POLICIES ?= $($(CONFIG)_POLICIES)
run-ripe: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
run-ripe: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
run-ripe:
	mkdir -p $(TEST_OUTPUT_DIR)/$(ARCH)
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(_DEBUG)_$(TEST_OUTPUT_FILE) $(XDIST) -k test_run_ripe ripe/ripe.py

ripe: build-policies build-ripe run-ripe

# avoid short-circuiting targets based on local file/dir names
.PHONY: build-policies

list: COLLECT_ONLY= --collect-only
list: run-tests

list-policies: COLLECT_ONLY= --collect-only
list-policies: build-policies

list-build: COLLECT_ONLY= --collect-only
list-build: build-tests

# Tests
clean-tests:
	rm -rf build/

build-tests: SOC_CFG ?= $($(CONFIG)_SOC_CFG)
build-tests: SIM ?= $($(CONFIG)_SIM)
build-tests: TESTS ?= $($(CONFIG)_TESTS)
build-tests: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-tests: ARCH ?= $($(CONFIG)_ARCH)
build-tests: MODULE ?= $($(CONFIG)_MODULE)
build-tests: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
build-tests: POLICIES ?= $($(CONFIG)_POLICIES)
build-tests: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-tests: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
build-tests: build-dirs
build-tests:
	$(PYTHON) -m pytest $(PYTEST_ARGS) $($(CONFIG)_PYTEST_ARGS)  --$(TEST_FORMAT)=$(CONFIG)_$(_DEBUG)_build_$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_build build_unit_tests.py

build-dirs: SOC_CFG ?= $($(CONFIG)_SOC_CFG)
build-dirs: SIM ?= $($(CONFIG)_SIM)
build-dirs: TESTS ?= $($(CONFIG)_TESTS)
build-dirs: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-dirs: ARCH ?= $($(CONFIG)_ARCH)
build-dirs: MODULE ?= $($(CONFIG)_MODULE)
build-dirs: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
build-dirs: POLICIES ?= $($(CONFIG)_POLICIES)
build-dirs: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
build-dirs:
	mkdir -p $(TEST_BUILD_DIR)/$(RUNTIME)/$(SOC_CFG)/log
	$(PYTHON) -m pytest $(PYTEST_ARGS) $($(CONFIG)_PYTEST_ARGS)  --$(TEST_FORMAT)=$(_DEBUG)_$(TEST_OUTPUT_FILE) $(COLLECT_ONLY) -k test_copy_build_dir build_unit_tests.py

tests: clean-tests build-tests

# PEX + policies
clean-policies:
	rm -rf pex/
	rm -rf policies/

build-policies: SOC_CFG ?= $($(CONFIG)_SOC_CFG)
build-policies: SIM ?= $($(CONFIG)_SIM)
build-policies: TESTS ?= $($(CONFIG)_TESTS)
build-policies: RUNTIME ?= $($(CONFIG)_RUNTIME)
build-policies: ARCH ?= $($(CONFIG)_ARCH)
build-policies: MODULE ?= $($(CONFIG)_MODULE)
build-policies: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
build-policies: POLICIES ?= $($(CONFIG)_POLICIES)
build-policies: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
build-policies: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
build-policies:
	mkdir -p policies/log
	mkdir -p pex
	mkdir -p pex/$(SIM)
	$(PYTHON) -m pytest $(PYTEST_ARGS) $($(CONFIG)_PYTEST_ARGS) --$(TEST_FORMAT)=$(CONFIG)_$(_DEBUG)_policy_$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_install_policy install_policies.py

policies: clean-policies build-policies

# run tests
run-tests: SOC_CFG ?= $($(CONFIG)_SOC_CFG)
run-tests: SIM ?= $($(CONFIG)_SIM)
run-tests: TESTS ?= $($(CONFIG)_TESTS)
run-tests: RUNTIME ?= $($(CONFIG)_RUNTIME)
run-tests: ARCH ?= $($(CONFIG)_ARCH)
run-tests: MODULE ?= $($(CONFIG)_MODULE)
run-tests: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
run-tests: POLICIES ?= $($(CONFIG)_POLICIES)
run-tests: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
run-tests: SOC_CFG ?= $($(CONFIG)_SOC_CFG)
run-tests: TIMEOUT ?= $($(CONFIG)_TIMEOUT)
run-tests: build-tests build-policies
	mkdir -p $(TEST_OUTPUT_DIR)/$(ARCH)
	$(PYTHON) -m pytest $(PYTEST_ARGS) $($(CONFIG)_PYTEST_ARGS) --$(TEST_FORMAT)=$(CONFIG)_$(_DEBUG)_run_$(TEST_OUTPUT_FILE) $(XDIST) $(COLLECT_ONLY) -k test_new run_unit_tests.py

PERFORMANCE_REPORT_ARGS = -r $(RUNTIME) -s $(SIM) --arch=$(ARCH) -p $(POLICIES) -t $(TESTS) -c $(if $(GPOLICIES),-g $(GPOLICIES),)

# generate performance report
performance-report: SOC_CFG ?= $($(CONFIG)_SOC_CFG)
performance-report: SIM ?= $($(CONFIG)_SIM)
performance-report: TESTS ?= performance
performance-report: RUNTIME ?= $($(CONFIG)_RUNTIME)
performance-report: ARCH ?= $($(CONFIG)_ARCH)
performance-report: MODULE ?= $($(CONFIG)_MODULE)
performance-report: GPOLICIES ?= $($(CONFIG)_GPOLICIES)
performance-report: POLICIES ?= $($(CONFIG)_POLICIES)
performance-report: XDIST ?= $($(CONFIG)_XDIST) # run in parallel
performance-report: SOC_CFG ?= $($(CONFIG)_SOC_CFG)
performance-report: TIMEOUT ?= 0
performance-report:
	TESTS=$(TESTS) TIMEOUT=$(TIMEOUT) $(MAKE) run-tests
	$(PYTHON) performance_report.py $(PERFORMANCE_REPORT_ARGS)

clean: clean-policies clean-tests
	rm -rf $(TEST_BUILD_DIR) $(TEST_OUTPUT_DIR) $(RIPE_CONFIGS) debug prof broken __pycache__ ripe/__pycache__ *.pyc assets report.html *report.xml prof_results.log .cache \
		tests/isp-runtime-frtos* tests/isp-runtime-bare*
	find tests/ -type f -name '*.o' -delete
