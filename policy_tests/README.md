Policy Testing
===================

Test code and script for automatic testing of policies.

Install Instructions
====================

   * Install py.test: `sudo apt-get install python-pytest`
   * Install py.test plugins:
       * `pip3 install pytest-html`
       * `pip3 install pytest-timeout`

   * Build policytool:
       * See README.md in policy-tool

Usage
=====

Run 'make' to kick off a test run using a default configuration. 

Internally, 'make' runs 3 different targets:

    'make build'  - compiles the test program(s) to be run
    'make kernel' - runs the policy tool to build the policy(s) to be run
    'make run'    - actually runs the test program(s) with the policy(s) in
    	            the simulator

There are several options that can be chosen to customize what policies and
programs are built and run during the test. These can be specified on the
command line:

    make TESTS=foo.c,bar.c // runs only foo.c and bar.c

or common configurations can be defined in the Makefile, i.e.

    # default QEMU build
    qemu: SIM=qemu
    qemu: RUNTIME=hifive
    qemu: MODULE=osv.hifive.main
    qemu: POLICIES=heap,none,rwx,stack,threeClass
    qemu: XDIST=-n 25 # run in parallel
    qemu: run

Each of the "knobs" available to configure a test run is described below:

Pytest config knobs -- 

  XDIST - How many workers to use when running tests in parallel.
    note: Variable must be '-n x' where x is the number you want, or 'auto'
    note: some things cannot be run in parallel. For example, running the
    	renode simulator and building the kernels are not currently supported
	in parallel

  ERROR_MSGS - how much info should print on failure? Options from pytest
    --tb=auto    # (default) 'long' tracebacks for the first and last
    		 # entry, but 'short' style for the other entries
    --tb=long    # exhaustive, informative traceback formatting
    --tb=short   # shorter traceback format
    --tb=line    # only one line per failure
    --tb=native  # Python standard library formatting
    --tb=no      # no traceback at all

Test program, kernel, & run common knobs -

  DEBUG - tell the subtasks to produce debugging output. What this actually
    	  does is up to the implementation of the subtask.

Test program build knobs --

  RUNTIME - what runtime environment to compile against? Supported examples:
    hifive - bare-metal runtime for hifive board
    frtos  - FreeRTOS

  TESTS - what test programs to run
    note: Positive tests should be listed in the 'tests' directory. The name of
    	  the test is the file or directory in which the test lives.

    note: Negative tests must be listed in a subdirectory of the 'tests'
    	  directory. In particular, if a test "x" should fail when run against
	  policy "a", it should be located in tests/a/x and the name of the
	  test is "a/x"

    note: Tests can be grouped in order to use a keyword such as "all" to
    	  run some subset of the available tests. These groups are defined in
	  test_groups.py. The name of the group should be a class name, while
	  the tests should be string entries in an array called "tests" within
	  the class. See the file for examples.

Policy kernel build knobs --

  MODULE -- an optional prefix to be applied to the POLICIES knob.

  POLICIES -- what policies to build

Test running knobs - 

  SIM - What simulator to run
    Currently supported simulators are 'qemu' and 'renode'

  COMPOSITE - What strategy for including composite policies?
    given policies a, b, and c: the following configs will produce policies:
      simple        - a, b, c, abc
      full          - a, b, c, ab, ac, bc, abc
      ANYTHING_ELSE - a, b, c

  RULE_CACHE - What model rule cache to simulate.
    options are ''(none), 'finite', 'infinite', and 'dmhc'
    
  RULE_CACHE_SIZE - size of rule cache

Output
======

The 'build' target creates an 'output/' directory that has subdirectories for
each test. Each test's subdirectory contains some build files including at
least a Makefile to compile the test, a 'src/' dir and a 'build/' dir for the
finished binary and build logs.

The 'kernels' target stores outputs from the policy-tool in subdirectories of
the 'kernels/' directory.

The 'run' target creates subdirectories in each test's directory. Each of
these subdirectories corresponds to a simulation run with a particular policy
for the test. It contains Makefiles, the policy kernel, run logs, and more.

Adding Tests
============

Tests should use the test_status functions to indicate test start and
pass fail status. The test status api can be found in the
`template/test_status.h` file.

The new test should be added to the 'all' group in test_groups.py 

Adding Knobs
============

Here we give an example of adding a new "knob" to the testing framework. This
is a diff of the patch that implemented the DEBUG knob, specifically for the
policy-tool (ie kernel target)

First, pytest has to know to look for the knob.

  diff --git a/policy_tests/conftest.py b/policy_tests/conftest.py
  index eaae11e..8141e1c 100644
  --- a/policy_tests/conftest.py
  +++ b/policy_tests/conftest.py
  @@ -27,0 +28,2 @@ def pytest_addoption(parser):
  +    parser.addoption('--isp_debug', default='no',
  +                     help='pass debug options to testing tasks (yes/no)')
  @@ -48,0 +51,4 @@ def composite(request):
  +@pytest.fixture
  +def debug(request):
  +    return 'yes' == request.config.getoption('--isp_debug')

Next, invocations of the makefile need to pass the value of the knob to pytest

  diff --git a/policy_tests/Makefile b/policy_tests/Makefile
  index afbb0b5..f846445 100644
  --- a/policy_tests/Makefile
  +++ b/policy_tests/Makefile
  @@ -12,0 +13 @@ RULE_CACHE_SIZE ?= 16
  +DEBUG ?= no
  @@ -14 +15 @@ RULE_CACHE_SIZE ?= 16
  -PYTEST_ARGS ?= -v -rs --timeout=180 $(ERROR_MSGS) --sim=$(SIM) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --policies=$(POLICIES) --composite=$(COMPOSITE) --module=$(MODULE)
  +PYTEST_ARGS ?= -v -rs --timeout=180 $(ERROR_MSGS) --sim=$(SIM) --isp_debug=$(DEBUG) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --policies=$(POLICIES) --composite=$(COMPOSITE) --module=$(MODULE)

Finally, subtasks can request the knob's value to be populated by pytest and
  can then use it for whatever task-specific operations it needs.

  diff --git a/policy_tests/install_kernels.py b/policy_tests/install_kernels.py
  index ba60f5b..df03c53 100644
  --- a/policy_tests/install_kernels.py
  +++ b/policy_tests/install_kernels.py
  @@ -17 +17 @@ import multiprocessing
  -def test_install_kernel(policy):
  +def test_install_kernel(policy, debug):
  @@ -29 +29 @@ def test_install_kernel(policy):
  -    doMkPolicy(policy)
  +    doMkPolicy(policy, debug)
  @@ -37 +37 @@ def test_install_kernel(policy):
  -def doMkPolicy(policy):
  +def doMkPolicy(policy, debug):
  @@ -45 +45,3 @@ def doMkPolicy(policy):
  +    if debug: # prepend debug flag/argument for policy tool
  +        ptarg.insert(0, "-d")


Debugging
=========

Policy Metadata aware debugging is supported on Renode and QEMU

This is acomplished with a variety of scripts and config files:
   * main.resc -- renode script file that configures the simulator and starts a GDB server
   * .gdbinit  -- GDB init script auto loaded into GDB creates metadata commands

Check out the test Makefile to see how GDB gets invoked.

Try this in GDB:

(gdb) help metadata 
Renode simulator commands:
   rstart   - renode start
   rquit    - renode quit
Metadata related commnads:
   pvm      - print violation message
   env-m    - get the env metadata
   reg-m n  - get register n metadata
   csr-m a  - get csr metadata at addr a
   mem-m a  - get mem metadata at addr a
Watchpoints halt simulation when metadata changes
   env-mw   - set watch on the env metadata
   reg-mw n - set watch on register n metadata
   csr-mw a - set watch on csr metadata at addr a
   mem-mw a - set watch on mem metadata at addr a

The GDB init script also advances the simulation to a breakpoint at main(), like this:

0x80000240 in _mstart ()
Breakpoint 1 at 0x80013f9c: file /home/andrew/dover-repos/policies/policy_tests/debug/osv.frtos.main.rwx-rwx_code_write_fails_1.c-O2/frtos.c, line 25.
Starting emulation...
No Policy Violation

Breakpoint 1, main ()
    at /home/andrew/dover-repos/policies/policy_tests/debug/osv.frtos.main.rwx-rwx_code_write_fails_1.c-O2/frtos.c:25
25	  xTaskCreate(main_task, "Main task", 1000, NULL, 1, NULL);

Edit .gdbinit if you need to debug startup code.

Now you can run your code. Here is what happens when you get a policy violation:

(gdb) c
Continuing.

Program received signal SIGTRAP, Trace/breakpoint trap.
Policy Violation:
    PC = 80008324    MEM = 800082e4
Metadata:
    Env   : {}
    Code  : {storeGrp, allGrp, Rd, Ex}
    Op1   : {}
    Op2   : {}
    Op3   : -0-
    Mem   : {immArithGrp, allGrp, notMemGrp, Rd, Ex}
Explicit Failure: write violation

0x80008328 in test_main ()
    at /home/andrew/dover-repos/policies/policy_tests/debug/osv.frtos.main.rwx-rwx_code_write_fails_1.c-O2/test.c:55
55	    *foo_ptr = foo;

This example is an attempted write to modify code, which is why code tags show up on Mem.

Try It
======

andrew@drone:~/dover-repos/policies/policy_tests$ make clean-kernels 
rm -rf /home/andrew/dover-install/kernels/*

andrew@drone:~/dover-repos/policies/policy_tests$ make install-kernels
install_kernels.py::test_simple[osv.frtos.main.nop] PASSED
install_kernels.py::test_simple[osv.frtos.main.rwx] PASSED
install_kernels.py::test_simple[osv.frtos.main.nop-rwx] PASSED

andrew@drone:~/dover-repos/policies/policy_tests$ make clean
rm -rf fail debug prof broken __pycache__ *.pyc assets report.html prof_results.log .cache

andrew@drone:~/dover-repos/policies/policy_tests$ make debug-osv.frtos.main.rwx-rwx_code_write_fails_1.c-O2
run_unit_tests.py::test_debug[osv.frtos.main.rwx-rwx_code_write_fails_1.c-O2] PASSED

cd debug/osv.frtos.main.rwx-rwx_code_write_fails_1.c-O2/

run each command in one of 3 new shells:

make renode-console
make gdb
make socat



