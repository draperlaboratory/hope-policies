This document seeks to explain how the build system in `policy_tests/`
works.

# Running an arbitrary C program

## Hacky approach

1.  First, build a dummy test.
    
        TEST=osv.frtos.main.rwx-stack-string_works_1.c-O2
        make debug-$TEST
    
    This will produce a number of outputs in the
    `debug/$TEST/build/` directory, one of which is `main`.

2.  Replace `main` with your own executable.

# How the build system works

## Deep dive into build system

### Makefile's `install-kernels` target

    install-kernels:
            $(PYTHON) -m pytest $(PYTEST_ARGS) -k test_simple install_kernels.py

When this recipe is executed, the following command is sent to the
shell.

    python3 -m pytest --timeout=180 --tb=no --sim=renode -v \
        --test_config=working -k test_simple install_kernels.py

Let's break this target down.  First, it invokes Python on the
`install_kernels.py` file with some options.

-   The `-m pytest` option causes Python to use the pytest module.
-   The `--test_config=working` option refers to `configs['working']`
    defined in `cfg_classes.py`, which is a reference to the
    `WorkingTests` class.
-   The `-k test_simple` option causes pytest to select the test
    named `test_simple`.

Digging into `install_kernels.py`, we see `test_simple(simpleF)`
invokes `doTest(simpleF)`.

-   The `doTest(osPolicyF)` function is defined in
    `install_kernels.py`. It invokes `doInstallPolicy()`, which is
    defined in `setup_test.py`.
    
    I set breakpoints on `doInstallPolicy()` in order to find out
    what its inputs look like. Here are some examples.
    
        # --- Invocation 1 ---
        osPol = ('osv.frtos.main.{pol}', ['none'], 'osv.frtos.main.none')
        installPath = 'kernel_dir/kernels/osv.frtos.main.none'
        
        # --- Invocation 2 ---
        osPol = ('osv.frtos.main.{pol}', ['rwx'], 'osv.frtos.main.rwx')
        installPath = 'kernel_dir/kernels/osv.frtos.main.rwx'
        
        # --- Invocation 3 ---
        osPol = ('osv.frtos.main.{pol}', ['stack'], 'osv.frtos.main.stack')
        installPath = 'kernel_dir/kernels/osv.frtos.main.stack'

### Makefile's `debug-$TEST` target

    debug-%:
            $(PYTHON) -m pytest $(PYTEST_ARGS) --$(TEST_FORMAT)=$(TEST_OUTPUT_FILE) -k test_debug[$*] run_unit_tests.py

## High level tasks performed by build system