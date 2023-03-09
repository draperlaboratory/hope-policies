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
        "hello_works_2",
        "ptr_arith_works_1",
        "malloc_prof_1",
        "malloc_prof_2",
        "malloc_works_1",
        "malloc_works_2",
        "malloc_works_3",
        "string_works_1",
        "longjump_works_1",
        "code_read_works_1",
        "inline_asm_works_1",
        "timer_works_1",
        "function_pointer_works_1",
        "function_pointer_works_2",
        "null_ptr_deref_fails_1",
        "rwx/code_write_fails_1",
        "rwx/data_exe_fails_1",
        "cfi/jump_data_fails_1",
        "heap/ptr_arith_fails_1",
        "heap/ptr_arith_fails_2",
        "heap/malloc_fails_1",
        "heap/malloc_fails_2",
        "heap/malloc_fails_3",
        "heap/use_after_free_fails_1",
        "heap/use_after_free_fails_2",
        "heap/double_free_fails_1",
        "heap/offset_free_fails_1",
        "stack/stack_fails_1",
        "threeClass/jump_data_fails_1",
        "threeClass/jump_non_calltgt_fails_1",
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
    ]

    tests64 = [
        "float_works",
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


class frtos(AllTests):
    tests = [test for test in AllTests.tests
                      if not any(test in s for s in
                                 [
                                  "heap-ppac-userType/webapp_patient_info_leak_fails",
                                  "password/webapp_password_leak",
				  "dhrystone/dhrystone-baremetal",
                                  "fft",
                                  "timer_works_1",
                                 ]
                                 )]


class frtos64(frtos):
    tests = frtos.tests + AllTests.tests64


class bare(AllTests):
    tests = [test for test in AllTests.tests
                      if not any(test in s for s in
                                 ["ping_pong_works_1",
                                  "dhrystone/dhrystone-baremetal",
				  "hello_works_2",
                                  "fft",
                                  "timer_works_1",
                                 ]
                                 )]


class bare64(bare):
    tests = bare.tests + AllTests.tests64


class mibench(AllTests):
    tests = [
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
    ]


class performance(AllTests):
    tests = mibench.tests + [
        "coremark",
        "dhrystone",
    ]

test_groups = {'all' : AllTests,
               'frtos' : frtos,
               'frtos64' : frtos64,
               'bare' : bare,
               'bare64' : bare64,
               'webapp' : webapp,
               'mibench' : mibench,
               'performance' : performance
}
