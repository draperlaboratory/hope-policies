# This silences python error trace backs, better for running tests set
# ERROR_MSGS to an empty string to print error trace backs
PYTHON ?= python3
ERROR_MSGS ?= --tb=long

TEST_FORMAT ?= junitxml
TEST_OUTPUT_FILE ?= report.xml

# default test config settings
COMPOSITE ?= simple
TESTS ?= all
RULE_CACHE_SIZE ?= 16

PYTEST_ARGS ?= -v -rs --timeout=180 $(ERROR_MSGS) --sim=$(SIM) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --policies=$(POLICIES) --composite=$(COMPOSITE) --modules=$(MODULE)

# TODO: find a way to report bad configs... maybe in pytest? ie no SIM set

# default QEMU build
qemu: SIM=qemu
qemu: RUNTIME=hifive
qemu: MODULE=osv.hifive.main
qemu: POLICIES=heap,none,rwx,stack,threeClass
qemu: XDIST=-n 25 # run in parallel
qemu: run

# default renode build
renode: SIM=renode
renode: RUNTIME=frtos
renode: MODULE=osv.frtos.main
renode: POLICIES=heap,none,rwx,stack
renode: run

build: 
	$(PYTHON) -m pytest $(PYTEST_ARGS)  --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) -n 25 -k test_build build_unit_tests.py

kernels:
	$(PYTHON) -m pytest $(PYTEST_ARGS) -k test_install_kernel install_kernels.py

run: build kernels
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_new run_unit_tests.py

list:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --collect-only run_unit_tests.py

list-kernels:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --collect-only install_kernels.py

clean: clean-kernels
	rm -rf output debug prof broken __pycache__ *.pyc assets report.html report.xml prof_results.log .cache

clean-kernels:
	rm -rf kernels/
