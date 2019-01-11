# test configuration classes
# be sure to add new configs to dict at bottom of this file

class AllTests:
    # Modify the following lists to add policies and test cases:

    #positive tests go in the tests dir
    tests = [
        "coremark",
        "printf_works_1.c",
        "hello_works_1.c",
        "stanford_int_treesort_fixed.c",
        "ping_pong_works_1.c",
        "link_list_works_1.c",
        "ptr_arith_works_1.c",
        "malloc_prof_1.c",
        "malloc_prof_2.c",
        "malloc_works_1.c",
        "malloc_works_2.c",
        "string_works_1.c",
        "longjump_works_1.c",
        "code_read_works_1.c",
        "timer_works_1.c",
        "function_pointer_works_1.c",
        "function_pointer_works_2.c",
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
        "taint/tainted_print_fails.c",
        "dhrystone7000.c",
    ]

class frtos(AllTests):
    tests = [test for test in AllTests.tests
                      if not any(test in s for s in
                                 ["timer_works_1.c",
                                  "coremark",
                                 ]
                                 )]

class hifive(AllTests):
    tests = [test for test in AllTests.tests
                      if not any(test in s for s in
                                 ["ping_pong_works_1.c",
                                  "dhrystone7000.c",
                                 ]
                                 )]

test_groups = {'all' : AllTests,
           'frtos' : frtos,
           'hifive' : hifive
}

