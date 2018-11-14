# This silences python error trace backs, better for running tests set
# ERROR_MSGS to an empty string to print error trace backs
PYTHON ?= python3
ERROR_MSGS ?= --tb=long
XDIST ?= 

KERNEL_DIR = kernel_dir
TEST_FORMAT ?= junitxml
TEST_OUTPUT_FILE ?= report.xml
SIM ?= 
RUNTIME ?= 
POLICIES ?= 
COMPOSITE ?= simple
TESTS ?= all
MODULES ?= 
RULE_CACHE ?=
RULE_CACHE_SIZE ?= 16
PYTEST_ARGS ?= -v --timeout=180 $(ERROR_MSGS) --sim=$(SIM) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --policies=$(POLICIES) --composite=$(COMPOSITE) --modules=$(MODULES)

qemu: SIM=qemu
qemu: RUNTIME=hifive
qemu: MODULES=osv.hifive.main
qemu: POLICIES=heap,none,rwx,stack,threeClass
qemu: XDIST=-n 25
qemu: run

renode: SIM=renode
renode: RUNTIME=frtos
renode: MODULES=osv.frtos.main
renode: POLICIES=heap,none,rwx,stack
renode: run

build: 
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) -n 25 -k test_build build_unit_tests.py

install-kernels:
	$(PYTHON) -m pytest $(PYTEST_ARGS) -k test_install_kernel install_kernels.py

run: build install-kernels
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_new run_unit_tests.py

# TODO: remove debug targets?
install-kernel-%:
	rm -rf $(KERNEL_DIR)/kernels/$*
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) -k test_kernel[$*] install_kernels.py

debug-%:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) -k test_debug[$*] run_unit_tests.py

list:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --collect-only run_unit_tests.py

list-kernels:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --collect-only install_kernels.py

clean: clean-kernels
	rm -rf output debug prof broken __pycache__ *.pyc assets report.html prof_results.log .cache

clean-kernels:
	rm -rf $(KERNEL_DIR)/kernels/*
