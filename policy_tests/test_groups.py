# test configuration classes
# be sure to add new configs to dict at bottom of this file

class AllTests:
    # Modify the following lists to add policies and test cases:

    #positive tests go in the tests dir
    tests = [
        "printf_works_1",
        "stanford_int_treesort_fixed",
        "ping_pong_works_1",
        "link_list_works_1",
        "hello_works_1",
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
        "webapp_admin_user_works",
        "webapp_patient_read_works",
        "heap-ppac-userType/webapp_unauth_doctor_routine_fails",
        "heap-ppac-userType/webapp_patient_info_leak_fails",
        "userType/webapp_double_usr_set",
        "password/webapp_password_leak",
        "bitcount",
        "adpcm_decode",
        "adpcm_encode",
        "aes",
        "rc4",
        "crc",
        "fft",
        "rsa",
        "dijkstra",
        "sha",
        "qsort",
        "randmath",
        "lzfx",
	"stringsearch",
	"blowfish",
	"limits",
    ]

class webapp(AllTests):
    tests = [
        "webapp_doctor_user_works",
        "webapp_admin_user_works",
        "webapp_patient_read_works",
        "heap-ppac-userType/webapp_unauth_doctor_routine_fails",
        "heap-ppac-userType/webapp_patient_info_leak_fails",
        "userType/webapp_double_usr_set",
        "password/webapp_password_leak",
    ]


# XXX: Re-enable Long-running tests once passing"
class frtos(AllTests):
    tests = [test for test in AllTests.tests
                      if not any(test in s for s in
                                 ["timer_works_1",
                                  "coremark",
                                  "stanford_int_treesort_fixed",
                                  "ping_pong_works_1",
                                  "malloc_prof_1",
                                  "malloc_prof_2",
                                  "taint/tainted_print_fails",
                                  "dhrystone7000",
                                  "webapp_doctor_user_works",
                                  "webapp_admin_user_works",
                                  "webapp_patient_read_works",
                                  "heap-ppac-userType/webapp_unauth_doctor_routine_fails",
                                  "heap-ppac-userType/webapp_patient_info_leak_fails",
                                  "userType/webapp_double_usr_set",
                                  "password/webapp_password_leak",
                                  "bitcount",
                                 ]
                                 )]


class bare(AllTests):
    tests = [test for test in AllTests.tests
                      if not any(test in s for s in
                                 [
                                  "ping_pong_works_1",
                                  "dhrystone7000",
                                  "hello_works_1",
                                 ]
                                 )]

test_groups = {'all' : AllTests,
               'frtos' : frtos,
               'bare' : bare,
               'webapp' : webapp
}

