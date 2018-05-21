
# This silences python error trace backs, better for running tests
ERROR_MSGS = --tb=no
# This allows python error trace backs, better for debugging scripts
#ERROR_MSGS =

simple:
	python -m pytest --html=report.html --timeout=180 $(ERROR_MSGS)  -v -k test_simple run_unit_tests.py

full:
	python -m pytest --html=report.html --timeout=180 $(ERROR_MSGS) -v -k test_full run_unit_tests.py

allOs:
	python -m pytest --html=report.html --timeout=180 $(ERROR_MSGS) -v -k test_all run_unit_tests.py

broken:
	python -m pytest $(ERROR_MSGS) -v -k test_broken run_unit_tests.py

debug-%:
	python -m pytest --html=report.html --timeout=180 $(ERROR_MSGS) -v -k test_debug[$*] run_unit_tests.py

profile:
	python -m pytest $(ERROR_MSGS) -v -k test_profile run_unit_tests.py

list:
	python -m pytest $(ERROR_MSGS) --collect-only run_unit_tests.py

install-kernels:
	python -m pytest --timeout=180 $(ERROR_MSGS) -v -k test_simple install_kernels.py

install-kernels-full:
	python -m pytest --timeout=180 $(ERROR_MSGS) -v -k test_full install_kernels.py

install-kernel-%:
	rm -rf $(DOVER)/kernels/$*
	python -m pytest --html=report.html --timeout=180 $(ERROR_MSGS) -v -k test_kernel[$*] install_kernels.py

list-kernels:
	python -m pytest --collect-only install_kernels.py

clean:
	rm -rf fail debug prof broken __pycache__ *.pyc assets report.html prof_results.log .cache

clean-kernels:
	rm -rf $(DOVER)/kernels/*
