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
        "hello_works_1",
        "hello_works_2",
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
        "dhrystone/dhrystone-baremetal",
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
        "picojpeg",
        "coremark",
        "dhrystone",
    ]

    testgenTests = [
        "all-combined/hope-testgen-tests/7_NumericErrors/234/numeric_error_234",
        "all-combined/hope-testgen-tests/7_NumericErrors/456p1/numeric_error_456p1",
        "all-combined/hope-testgen-tests/7_NumericErrors/456p2/numeric_error_456p2",
        "all-combined/hope-testgen-tests/7_NumericErrors/456p3/numeric_error_456p3",
        "all-combined/hope-testgen-tests/7_NumericErrors/457p1/numeric_error_457p1",
        "all-combined/hope-testgen-tests/7_NumericErrors/457p2/numeric_error_457p2",
        "all-combined/hope-testgen-tests/7_NumericErrors/475/numeric_error_475",
        "all-combined/hope-testgen-tests/7_NumericErrors/665p1/numeric_error_665p1",
        "all-combined/hope-testgen-tests/7_NumericErrors/665p2/numeric_error_665p2",
        "all-combined/hope-testgen-tests/7_NumericErrors/686/numeric_error_686",
        "all-combined/hope-testgen-tests/7_NumericErrors/687/numeric_error_687",
        "all-combined/hope-testgen-tests/7_NumericErrors/824p1/numeric_error_824p1",
        "all-combined/hope-testgen-tests/7_NumericErrors/824p2/numeric_error_824p2",
        # "all-combined/hope-testgen-tests/5_InformationLeakage/atoi_cached_biinterpreter", # This test crashes :'(
        "all-combined/hope-testgen-tests/5_InformationLeakage/atoi_flatstore_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/atoi_fragmented_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/atoi_separate_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/atoi_cached_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/atoi_flatstore_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/atoi_fragmented_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/atoi_separate_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/cache_cached_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/cache_flatstore_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/cache_fragmented_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/cache_separate_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/cache_cached_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/cache_flatstore_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/cache_fragmented_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/cache_separate_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/classifydeclassify_cached_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/classifydeclassify_flatstore_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/classifydeclassify_fragmented_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/classifydeclassify_separate_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/classifydeclassify_cached_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/classifydeclassify_flatstore_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/classifydeclassify_fragmented_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/classifydeclassify_separate_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/directsys_cached_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/directsys_flatstore_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/directsys_fragmented_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/directsys_separate_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/directsys_cached_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/directsys_flatstore_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/directsys_fragmented_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/directsys_separate_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/error_cached_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/error_flatstore_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/error_fragmented_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/error_separate_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/error_cached_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/error_flatstore_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/error_fragmented_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/error_separate_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing_cached_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing_flatstore_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing_fragmented_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing_separate_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing_cached_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing_flatstore_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing_fragmented_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing_separate_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing2_cached_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing2_flatstore_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing2_fragmented_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing2_separate_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing2_cached_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing2_flatstore_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing2_fragmented_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/indexing2_separate_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/loginmsg_cached_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/loginmsg_flatstore_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/loginmsg_fragmented_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/loginmsg_separate_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/loginmsg_cached_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/loginmsg_flatstore_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/loginmsg_fragmented_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/loginmsg_separate_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/systemconfig_separate_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/systemconfig_fragmented_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/systemconfig_flatstore_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/systemconfig_cached_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/systemconfig_separate_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/systemconfig_fragmented_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/systemconfig_flatstore_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/systemconfig_cached_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/markprivate_separate_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/markprivate_fragmented_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/markprivate_flatstore_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/markprivate_cached_simpleatoi",
        "all-combined/hope-testgen-tests/5_InformationLeakage/markprivate_separate_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/markprivate_fragmented_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/markprivate_flatstore_biinterpreter",
        "all-combined/hope-testgen-tests/5_InformationLeakage/markprivate_cached_biinterpreter",
        # "all-combined/hope-testgen-tests/1_BufferErrors/01", # Invalid Test
        "all-combined/hope-testgen-tests/1_BufferErrors/02",
        "all-combined/hope-testgen-tests/1_BufferErrors/03",
        # "all-combined/hope-testgen-tests/1_BufferErrors/04", # Invalid Test
        "all-combined/hope-testgen-tests/1_BufferErrors/05",
        "all-combined/hope-testgen-tests/1_BufferErrors/06",
        # "all-combined/hope-testgen-tests/1_BufferErrors/07", # Invalid Test
        # "all-combined/hope-testgen-tests/1_BufferErrors/08", # Invalid Test
        "all-combined/hope-testgen-tests/1_BufferErrors/09",
        "all-combined/hope-testgen-tests/1_BufferErrors/10",
        "all-combined/hope-testgen-tests/1_BufferErrors/11",
        "all-combined/hope-testgen-tests/1_BufferErrors/12",
        "all-combined/hope-testgen-tests/1_BufferErrors/13",
        "all-combined/hope-testgen-tests/1_BufferErrors/14",
        "all-combined/hope-testgen-tests/1_BufferErrors/15",
        # "all-combined/hope-testgen-tests/1_BufferErrors/16", # Invalid Test
        "all-combined/hope-testgen-tests/1_BufferErrors/18",
        "all-combined/hope-testgen-tests/1_BufferErrors/17",
        "all-combined/hope-testgen-tests/1_BufferErrors/19",
        "all-combined/hope-testgen-tests/1_BufferErrors/20",
        "all-combined/hope-testgen-tests/1_BufferErrors/21",
        "all-combined/hope-testgen-tests/1_BufferErrors/22",
        "all-combined/hope-testgen-tests/1_BufferErrors/23",
        "all-combined/hope-testgen-tests/1_BufferErrors/24",
        "all-combined/hope-testgen-tests/1_BufferErrors/25",
    ]

    # List of tests that are failing because no policy catches them.
    failingTests = [
        "all-combined/hope-testgen-tests/1_BufferErrors/02",
        "all-combined/hope-testgen-tests/1_BufferErrors/17",
        "all-combined/hope-testgen-tests/1_BufferErrors/23",
        "all-combined/hope-testgen-tests/1_BufferErrors/25",
        "all-combined/hope-testgen-tests/7_NumericErrors/234/numeric_error_234",
        "all-combined/hope-testgen-tests/7_NumericErrors/456p1/numeric_error_456p1",
        "all-combined/hope-testgen-tests/7_NumericErrors/456p2/numeric_error_456p2",
        "all-combined/hope-testgen-tests/7_NumericErrors/456p3/numeric_error_456p3",
        "all-combined/hope-testgen-tests/7_NumericErrors/457p1/numeric_error_457p1",
        "all-combined/hope-testgen-tests/7_NumericErrors/457p2/numeric_error_457p2",
        "all-combined/hope-testgen-tests/7_NumericErrors/665p1/numeric_error_665p1",
        "all-combined/hope-testgen-tests/7_NumericErrors/665p2/numeric_error_665p2",
        "all-combined/hope-testgen-tests/7_NumericErrors/686/numeric_error_686",
        "all-combined/hope-testgen-tests/7_NumericErrors/824p1/numeric_error_824p1",
        "all-combined/hope-testgen-tests/7_NumericErrors/824p2/numeric_error_824p2",
    ]
    
    # Tests that should be run only against all policies simultaneously.
    combinedPolicyTests = testgenTests + []

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


class frtos(AllTests):
    tests = [test for test in AllTests.tests + AllTests.combinedPolicyTests
                      if not any(test in s for s in
                                 [
                                  "heap-ppac-userType/webapp_patient_info_leak_fails",
                                  "password/webapp_password_leak",
                                  "fft",
                                  "timer_works_1",
                                  "dhrystone/dhrystone-baremetal",
                                 ]
                                 )]


class testgen(AllTests):
    tests = [test for test in AllTests.combinedPolicyTests
                      if not any(test in s for s in
                                 [
                                  "heap-ppac-userType/webapp_patient_info_leak_fails",
                                  "password/webapp_password_leak",
                                  "fft",
                                  "timer_works_1",
                                  "dhrystone/dhrystone-baremetal",
                                 ]
                                 )]

class bare(AllTests):
    tests = [test for test in AllTests.tests + AllTests.combinedPolicyTests
                      if not any(test in s for s in
                                 ["ping_pong_works_1",
                                  "dhrystone/dhrystone-baremetal",
                                  "hello_works_2",
                                  "fft",
                                  "timer_works_1",
                                  "hello_works_2",
                                 ] + AllTests.testgenTests
                                 )]

test_groups = {'all' : AllTests,
               'frtos' : frtos,
               'bare' : bare,
               'webapp' : webapp,
               'testgen' : testgen,
}
