

Policy Testing
===================

Test code and script for automatic testing of policies.

Install Instructions
====================

   * Install py.test: `sudo apt-get install python-pytest`
   * Install py.test plugins:
       * `pip2 install pytest-html`
       * `pip2 install pytest-timeout`

   * Create env var `DOVER` points to: `/home/user_name/dover-install`
   * Create env var `DOVER_SOURCES` that points to: `/home/user_name/dover-repos`
   * Create env var `FREE_RTOS_DIR` that points to: `/home/user_name/dover-repos/FreeRTOS`

   * Build policytool:
       * See README.md in policy-tool

Simulator
=========

Currently the test script supports three simulators.

   * Renode
   * Verilator (Broken currently)
   * FPGA (Broken currently)
   
To select between simulation targets you need to edit the simulator variable
at the top of the `cfg_test.py` script in `policy_tests`.

Note: For the FPGA target you need to modify dover-os to use the
MM_1M_auto memory configuration.

Usage ======

First, select a set of tests to run via the test configuration var `cfg` in
cfg_test.py. Test configurations are defined in testClasses.py

Second, the kernels for the test need to be build and installed to dover-install

`make list-kernels` -- lists all kernel combinations that will be built
`make clean-kernels` -- remove all kernels from dover-install
`make install-kernels` -- build all kernel combinations and install them

The test script isn't designed to be run by pytest directly, it is
intended to be called from the Makefile.

`make list` -- lists all availible tests
`make full` -- run all tests with only -O2 gcc flag (Default make target)
`make simple` -- run all tests with each individual policy by itself, no composite policies
`make allOs` -- run all tests with -O1 -O2 -O3 gcc flags
`make debug-xxxx` -- Where xxxx is a test name as printed in make list inside []
                     runs the specified test in the debug dir not fail dir

Tests can be either positive (expected to pass) or negative (expected
to get a policy violation, after the call to `begin_test`). The test
name string used in the debug target is constructed from: policies-dir_filename-optlevel, where
dir is used for negative tests only.

    * `Stack-hello_works_1.c-O2` -- Positive test, Stack policy, hello_works_1.c, compiled with gcc -O2
    * `RWX.Stack-ptr_arith_works_1.c-O2` -- Positive test, RWX and Stack policies...
    * `Stack-Stack_ptr_arith_fails_1.c-O2` -- Negative test, Stack policy, Stack dir, ptr_arith_fails_1.c...
    * `none-hello_works_1.c-O2` -- Positive test, no policy...

Policies must be listed in alphabetic order to use the debug
target. After the test runs a complete test dir will be found in the
debug dir.

Adding Tests
============

Open `testClasses.py` and create a new configuration class with the
tests and add the class to the `config` dict.

Tests need to use the test_status functions to indicate test start and
pass fail status. The test status api can be found in the
`template/test_status.h` file.

Notes
=====

Each test is run in its own dir inside of policy_tests/fail. If variable
removePassing is set to True the test directories for passing tests
will be removed.  Failing tests are left in the `policy_tests/fail` dir
with a log file and a Makefile that can be used to rerun the test.

All permutations of policies are tested with the positive test
cases. Negative test cases need to be run with a specific policy,
therefore note the following convention:

    * All positive test cases go into `policy_tests/tests/` dir
    * Negative tests go into policy specific sub-folders, e.g. `policy_tests/tests/RWX/`. 
      The test script matches the dir name with the policy prefix to exclude tests that 
      don't have the necessary policy for the test.

Debugging
=========

Policy Metadata aware debugging is supported on Renode

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



