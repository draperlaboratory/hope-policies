# Policy Testing

Test code and script for automatic testing of policies.

# Install Instructions

   * Install py.test: `sudo apt-get install python-pytest`
   * Install py.test plugins:
       * `pip3 install pytest-html`
       * `pip3 install pytest-timeout`

   * Build policytool:
       * See README.md in policy-tool

# Usage

Run `make` to kick off a test run using a default configuration. 

Internally, 'make' runs 3 different targets:

- build-tests    - compiles the test program(s) to be run
- build-policies - runs the policy tool to build the policy(s) to be run
- run-tests      - runs the test program(s) with the policy(s) in the simulator

There are several options that can be chosen to customize what policies and
programs are built and run during the test. These can be specified on the
command line:

    make POLICIES=heap // runs only heap policy tests

or common configurations can be defined in the Makefile. You will typically
need to define at least SIM, TESTS, RUNTIME, MODULE, and POLICIES to specify enough
to create a full run of tests without errors. The common configuration should
be given a name, variables should be named `name_VAR`. With this done, setting
CONFIG=name will invoke the tests with the specified variables. This can be
called quickly from the command line with a target-specific config variable.
See the example below to clarify this process:

    # simple qemu build
    qemu_SIM = qemu
    qemu_TESTS = bare
    qemu_RUNTIME = bare
    qemu_MODULE = osv.bare.main
    qemu_POLICIES = heap,none,rwx,stack,threeClass
    qemu_XDIST = -n 25 # run in parallel
    qemu: CONFIG=qemu
    qemu: all

## Knobs to configure the test runs

### Pytest config knobs

- JOBS: How many workers to use when running tests in parallel.
   - note: some things cannot be run in parallel. For example, running the
     renode simulator and building the policies are not currently supported in
     parallel. In the makefile, the variable XDIST is set to pass
     configuration for $(JOBS) workers. As such, XDIST should be left blank
     in order to avoid parallelization.

- ERROR_MSGS: how much info should print on failure? Options from pytest
   - --tb=auto    # (default) 'long' for first & last entry, otherwise 'short'
   - --tb=long    # exhaustive, informative traceback formatting
   - --tb=short   # shorter traceback format
   - --tb=line    # only one line per failure
   - --tb=native  # Python standard library formatting
   - --tb=no      # no traceback at all

### Test program, policy, & run common knobs

- DEBUG - tell the subtasks to produce debugging output. What this actually
    	  does is up to the implementation of the subtask. (yes/no)

### Test program build knobs

- RUNTIME: what runtime environment to compile against? Supported examples:
   - bare - bare-metal runtime
   - frtos - FreeRTOS runtime

- TESTS: what test programs to run
   - note: Positive tests should be listed in the 'tests' directory. The name
     of the test is the file or directory in which the test lives.
   - note: Negative tests must be listed in a subdirectory of the 'tests'
     directory. In particular, if a test "x" should fail when run against
     policy "a", it should be located in tests/a/x and the name of the
     test is "a/x"
   - note: Tests can be grouped in order to use a keyword such as "all" to
     run some subset of the available tests. These groups are defined in
     test_groups.py. The name of the group should be a class name, while
     the tests should be string entries in an array called "tests" within
     the class. See the file for examples.

### Policy build knobs

- MODULE: an optional prefix to be applied to the POLICIES knob.

- POLICIES: what policies to build

### Test running knobs

- SIM: What simulator to run
   - Currently supported simulators are 'qemu' and 'renode'

- COMPOSITE: What strategy for including composite policies?
   - given policies a, b, and c: the following configs will produce policies:
      - simple        - a, b, c, abc
      - full          - a, b, c, ab, ac, bc, abc
      - ANYTHING_ELSE - a, b, c

- RULE_CACHE: What model rule cache to simulate.
   - options are ''(none), 'finite', 'infinite', and 'dmhc'
    
- RULE_CACHE_SIZE: size of rule cache

# Output

The `build` target creates an `output/` directory that has subdirectories for
each test. Each test's subdirectory contains some build files including at
least a Makefile to compile the test, a `src/` dir and a `build/` dir for the
finished binary and build logs.

The `policies` target stores outputs from the policy-tool in subdirectories of
the `policies/` directory.

The `run` target creates subdirectories in each test's directory. Each of
these subdirectories corresponds to a simulation run with a particular policy
for the test. It contains Makefiles, the policy, run logs, and more.

Summary of output directories and files, their purpose, and the build target
responsible for generating them:

|file                        | description/notes                     | target   |
|----------------------------|---------------------------------------|--------  |
|`policies/`                 | contains compiled policies            | policies |
|`..compiled_policy_1/`      | output of policy tool for policy 1    | policies |
|`pex/`                      | contains compiled PEX binaries        | policies |
|`..compiled_pex_1`          | compiled PEX binary                   | policies |
|`output/`                   | tests binaries & simulation run output| build    |
|`..test_1/`                 | all files related to test_1           | build    |
|`....Makefile`              | build test_1 binary                   | build    |
|`....test_1.entities.yml`   | test-specific policy config           | build    |
|`....runX.py`               | script to run simulator X with test_1 | run      |
|`....srcs/`                 | test 1 + ISP wrappers source code     | build    |
|`......test_1.c`            |                                       | build    |
|`......test_status.c`       |                                       | build    |
|`......test_status.h`       |                                       | build    |
|`......    ...`             |                                       | build    |
|`....build/`                |                                       | build    |
|`......Makefile`            | used build test_1 binary              | build    |
|`......main`                | test_1 binary                         | build    |
|`......build.log`           | output of test_1 compilation          | build    |
|`....policy_1/`             | test_1 & policy_1 simulation output   | run      |
|`......Makefile`            | run tagging tools or simulation       | run      |
|`......compiled_policy_1/`  | copied from policies/                 | run     |
|`......bininfo/`            | test_1 & policy_1 tagging tool output | run      |
|`........main.text`         | asm of compiled binary                | run      |
|`........main.test.tagged`  | tagged asm of compiled binary         | run      |
|`........main.taginfo`      | initial tag state for binary          | run      |
|`......inits.log`           | output of tagging tools               | run      |
|`......sim.log`             | output of simulator for run           | run      |
|`......pex.log`             | PEX policy output during simulation   | run      |
|`......uart.log`            | target UART output during simulation  | run      |

# Adding Tests

Tests should use the test_status functions to indicate test start and
pass fail status. The test status api can be found in the
`template/test_status.h` file.

The new test should be added to the `all` group in `test_groups.py`

# Adding Knobs

Here we give an example of adding a new "knob" to the testing framework. This
is a diff of the patch that implemented the DEBUG knob, specifically for the
policy-tool (ie policy target)

First, pytest has to know to look for the knob.

  ```
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
  ```
 
Next, invocations of the makefile need to pass the value of the knob to pytest

  ```
  diff --git a/policy_tests/Makefile b/policy_tests/Makefile
  index afbb0b5..f846445 100644
  --- a/policy_tests/Makefile
  +++ b/policy_tests/Makefile
  @@ -12,0 +13 @@ RULE_CACHE_SIZE ?= 16
  +DEBUG ?= no
  @@ -14 +15 @@ RULE_CACHE_SIZE ?= 16
  -PYTEST_ARGS ?= -v -rs --timeout=180 $(ERROR_MSGS) --sim=$(SIM) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --policies=$(POLICIES) --composite=$(COMPOSITE) --module=$(MODULE)
  +PYTEST_ARGS ?= -v -rs --timeout=180 $(ERROR_MSGS) --sim=$(SIM) --isp_debug=$(DEBUG) --test=$(TESTS) --rule_cache=$(RULE_CACHE) --rule_cache_size=$(RULE_CACHE_SIZE) --runtime=$(RUNTIME) --policies=$(POLICIES) --composite=$(COMPOSITE) --module=$(MODULE)
  ```

Finally, subtasks can request the knob's value to be populated by pytest and
can then use it for whatever task-specific operations it needs.

  ```
  diff --git a/policy_tests/install_policies.py b/policy_tests/install_policies.py
  index ba60f5b..df03c53 100644
  --- a/policy_tests/install_policies.py
  +++ b/policy_tests/install_policies.py
  @@ -17 +17 @@ import multiprocessing
  -def test_install_policy(policy):
  +def test_install_policy(policy, debug):
  @@ -29 +29 @@ def test_install_policy(policy):
  -    doMkPolicy(policy)
  +    doMkPolicy(policy, debug)
  @@ -37 +37 @@ def test_install_policy(policy):
  -def doMkPolicy(policy):
  +def doMkPolicy(policy, debug):
  @@ -45 +45,3 @@ def doMkPolicy(policy):
  +    if debug: # prepend debug flag/argument for policy tool
  +        ptarg.insert(0, "-d")
  ```

# Running Individual Tests

An `isp_run_app` helper script is provided to make running individual test/policy
scenarios easier.  For example the data execute fails test with the RWX policy,
can be run with:

```
mkdir test-output
isp_run_app build/hifive/rwx/data_exe_fails_1 -p rwx -r hifive -o ./test-output
```

See the commands help output for further information.

# RIPE tests

There is another target included in the Makefile to run RIPE tests. RIPE (the
Runtime Intrusion Detection Evaluator) is designed to execute different memory
corruption vulnerabilities within its process space. It is intended to be a
tool to test the coverage of security architectures.

`make ripe` will run the RIPE test with over 100 different attacks. Each of
these attacks may run with 1 or more policies that are expected to stop the
attack. By default, all RIPE tests that are run are "negative" tests. In other
words, a policy violation is expected for every ripe test that is run.

As implemented currently, the RIPE attack configurations are not fully
parameterized within pytest. Instead, the `ripe/gen_ripe_congigs.py` script
outputs all supported attack configurations along with the policies that are
expected to protect against each configuration. Note that the policies _are_
parameterized with pytest. In other words, the regular pytest configurations
(`POLICIES` and `MODULES` as discussed elsewhere in this document) are used
to determine which policies _could_ be run against the ripe tests in a
particular ripe test run, and those policies listed with each configuration in
ripe_configs.py are used by pytest to determine whether to run or skip a given
configuration/policy combination.

Output from the ripe tests goes in `output/ripe/`.

Note that one major weakness of the RIPE testing as currently implemented is
that the inability to pass arguments to the binary when it runs. This means
that the configuration needs to be set at compile time, which demands that the
RIPE binary be compiled separately for each of the 100+ test configurations,
even though the only thing that changes are 5 configuration variables.

# Debugging

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

## Debugging Helpers

An `isp_debug` helper script is provided to simplify debugging.  To use
it simply append the debug port option to the `isp_run_app` command invocation
and invoke the `isp_debug` command from a separate terminal with appropriate
arguments.

```
isp_run_app ... -g 3333
isp_debug build/hifive/rwx/data_exe_fails_1 3333
```

See the commands help output for further information.

## Example - Register Watchpoints

This example demonstrates setting a register watchpoint by monitoring the
register that the tainted global variable is loaded into.

```
mkdir -p test-output
isp_run_app build/hifive/taint/tainted_print_fails -p taint -r hifive -o test-output/ -g 3333
isp_debug build/hifive/taint/tainted_print_fails 3333
(gdb) reg-m 11
 {} 
(gdb) reg-mw 11
(gdb) c
(gdb) reg-m 11
 {Taint} 
```

## Example - Memory Watchpoints

This example demonstrates setting a memory watchpoint by monitoring the
heap region that is used to allocate a 32-byte object.

```
mkdir -p test-output
isp_run_app build/hifive/heap/malloc_fails_1 -p heap -r hifive -o test-output/ -g 3333
isp_debug build/hifive/heap/malloc_fails_1 3333
(gdb) p/x ((((int)(&ucHeap) + 0x0000001F) >> 5) << 5)
(gdb) $21 = 0x80000a20
(gdb) mem-m 0x80000a20
 {RawHeap}
(gdb) mem-mw 0x80000a20
(gdb) c
Continuing.

Program received signal SIGTRAP, Trace/breakpoint trap.
 No Policy Violation 
dover_tag (ptr=<optimized out>, bytes=<optimized out>)
    at isp-runtime-hifive/bsp/libwrap/stdlib/malloc.c:159
159	    p++;
(gdb) mem-m 0x80000a20
 {Cell 0x0}
```
