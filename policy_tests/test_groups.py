# test configuration classes
# be sure to add new configs to dict at bottom of this file

class AllTests:
    # Modify the following lists to add policies and test cases:

    #positive tests go in the tests dir
    tests = [
        "printf_works_1",
        "hello_works_1",
        "stanford_int_treesort_fixed",
        "ping_pong_works_1",
        "link_list_works_1",
        "ptr_arith_works_1",
        "malloc_prof_1",
        "malloc_prof_2",
        "malloc_works_1",
        "malloc_works_2",
        "string_works_1",
        "longjump_works_1",
        "code_read_works_1",
        "timer_works_1",
        "function_pointer_works_1",
        "function_pointer_works_2",
        "rwx/code_write_fails_1", 
        "rwx/data_exe_fails_1", 
        "cfi/jump_data_fails_1",
        "heap/ptr_arith_fails_1",
        "heap/ptr_arith_fails_2",
        "heap/malloc_fails_1",
        "heap/malloc_fails_2",
        "heap/malloc_fails_3",
        "stack/stack_fails_1",
        "threeClass/jump_data_fails_1",
        "threeClass/call_fails_1",
        "taint/tainted_print_fails",
        "dhrystone7000",
        "webapp_doctor_user_works",
        "heap-ppac-usr_type/webapp_patient_user_fails",
        "usr_type/webapp_double_usr_set",
        "password/webapp_password_leak",
    ]

class frtos(AllTests):
    tests = [test for test in AllTests.tests
                      if not any(test in s for s in
                                 ["timer_works_1",
                                  "coremark",
                                 ]
                                 )]

class hifive(AllTests):
    tests = [test for test in AllTests.tests
                      if not any(test in s for s in
                                 ["ping_pong_works_1",
                                  "dhrystone7000",
                                 ]
                                 )]

test_groups = {'all' : AllTests,
           'frtos' : frtos,
           'hifive' : hifive
}

