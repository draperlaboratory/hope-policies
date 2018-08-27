# test configuration classes
# be sure to add new configs to dict at bottom of this file

class AllTests:
    # Modify the following lists to add policies and test cases:

    # list of module hierarchies in python string format syntax.
    # {pol} gets replaced with one of the policies from below
    os_modules = ["osv.frtos.main.{pol}", "osv.hifive.main.{pol}"]

    # policies to test
    policies = ["none", "cfi", "nop", "rwx", "stack", "heap", "threeClass"]

    #positive tests go in the tests dir
    positive_tests = [
        "printf_works_1.c",
        "hello_works_1.c",
        "stanford_int_treesort_fixed.c",
        "ping_pong_works_1.c",
        "link_list_works_1.c",
        "ptr_arith_works_1.c",
        "malloc_works_1.c",
        "malloc_works_2.c",
        "string_works_1.c",
        "longjump_works_1.c",
        "code_read_works_1.c",
        "timer_works_1.c",
        "function_pointer_works_1.c",
        "function_pointer_works_2.c"
    ]

    # negative tests need to be in a dir that matches the policy 
    #    that is expected to fail
    negative_tests = [
        "rwx/code_write_fails_1.c", 
        "rwx/data_exe_fails_1.c", 
        "cfi/jump_data_fails_1.c",
        "heap/ptr_arith_fails_1.c",
        "heap/ptr_arith_fails_2.c",
        "heap/malloc_fails_1.c",
        "heap/malloc_fails_2.c",
        "heap/malloc_fails_3.c",
        "stack/stack_fails_1.c",
        "threeClass/jump_data_fails_1.c",
        "threeClass/call_fails_1.c",
    ]

class CFIRWXTests(AllTests):
    # Modify the following lists to add policies and test cases:
    # policies to test
    policies = ["cfi-rwx"]

    # negative tests need to be in a dir that matches the policy
    #    that is expected to fail
    negative_tests = [
        "rwx/code_write_fails_1.c",
        "rwx/data_exe_fails_1.c",
        "cfi/jump_data_fails_1.c",
    ]

class WorkingTests(AllTests):
    os_modules = ["osv.frtos.main.{pol}"]
    policies = ["none", "rwx", "stack"]
    positive_tests = [test for test in AllTests.positive_tests
                      if not any(test in s for s in
                                 ["timer_works_1.c"
                                  "longjump_works_1.c"
                                 ]
                                 )]
    negative_tests = [
        "rwx/code_write_fails_1.c",
        "rwx/data_exe_fails_1.c",
        "threeClass/jump_data_fails_1.c",
        "threeClass/call_fails_1.c",
        "stack/stack_fails_1.c",
    ]

class DebugTests(AllTests):
    os_modules = ["osv.frtos.main.{pol}"]
    policies = ["rwx"]
    positive_tests = [ "hello_works_1.c" ]
    negative_tests = [ ]


class FRTOSTests(AllTests):
    os_modules = ["osv.frtos.main.{pol}"]


class HifiveTests(AllTests):
    os_modules = ["osv.hifive.main.{pol}"]
    policies = ["none", "rwx", "stack", "threeClass"]
    positive_tests = [test for test in AllTests.positive_tests
                      if not any(test in s for s in
                                 ["ping_pong_works_1.c",
                                  "longjump_works_1.c"
                                  "stanford_int_treesort_fixed.c"
                                 ]
                                 )]
    negative_tests = [
        "rwx/code_write_fails_1.c",
        "rwx/data_exe_fails_1.c",
        "threeClass/jump_data_fails_1.c",
        "threeClass/call_fails_1.c",
        "stack/stack_fails_1.c",
    ]

configs = {'all' : AllTests,
           'working' : WorkingTests,
           'debug' : DebugTests,
           'frtos' : FRTOSTests,
           'cfirwx' : CFIRWXTests,
           'hifive' : HifiveTests
}

