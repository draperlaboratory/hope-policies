# This silences python error trace backs, better for running tests set
# ERROR_MSGS to an empty string to print error trace backs
PYTHON ?= python3
ERROR_MSGS ?= --tb=long
XDIST ?= -n auto

KERNEL_DIR = kernel_dir
TEST_FORMAT ?= junitxml
TEST_OUTPUT_FILE ?= report.xml
SIM ?= qemu
CONFIG ?= hifive
REMOVE_PASSING ?= #--remove_passing
PYTEST_ARGS ?= --timeout=180 $(ERROR_MSGS) --sim=$(SIM) -v --test_config=$(CONFIG) $(REMOVE_PASSING)

simple:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_simple run_unit_tests.py

full:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_full run_unit_tests.py

allOs:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) $(XDIST) -k test_all run_unit_tests.py

broken:
	$(PYTHON) -m pytest $(ERROR_MSGS) -v -k test_broken run_unit_tests.py

debug-%:
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) -k test_debug[$*] run_unit_tests.py

profile:
	$(PYTHON) -m pytest $(ERROR_MSGS) $(XDIST) -v -k test_profile run_unit_tests.py

list:
	$(PYTHON) -m pytest $(ERROR_MSGS) --collect-only run_unit_tests.py

install-kernels:
	$(PYTHON) -m pytest $(PYTEST_ARGS) -k test_simple install_kernels.py

install-kernels-full:
	$(PYTHON) -m pytest $(PYTEST_ARGS) -k test_full install_kernels.py

install-kernel-%:
	rm -rf $(KERNEL_DIR)/kernels/$*
	$(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) -k test_kernel[$*] install_kernels.py

list-kernels:
	$(PYTHON) -m pytest --collect-only install_kernels.py

clean: clean-kernels
	rm -rf fail debug prof broken __pycache__ *.pyc assets report.html prof_results.log .cache

clean-kernels:
	rm -rf $(KERNEL_DIR)/kernels/*
