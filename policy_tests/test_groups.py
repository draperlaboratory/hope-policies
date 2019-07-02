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
        "dhrystone/dhrystone-baremetal",
        "webapp_doctor_user_works",
        "webapp_admin_user_works",
        "webapp_patient_read_works",
        "heap-ppac-userType/webapp_unauth_doctor_routine_fails",
        "heap-ppac-userType/webapp_patient_info_leak_fails",
        "userType/webapp_double_usr_set",
        "password/webapp_password_leak",
        "bitcount",
        "crc",
        "fft",
        "limits",
        "randmath",
        "rc4",
        "qsort",
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

class rhealstone(AllTests):
    tests = [
        "rhealstone_switching",
        "rhealstone_deadlk_base",
        "rhealstone_deadlk_test",
        "rhealstone_interrupt",
        "rhealstone_intertask",
        "rhealstone_preempt",
        "rhealstone_sem_base",
        "rhealstone_sem_test",
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
                                  "webapp_doctor_user_works",
                                  "webapp_admin_user_works",
                                  "webapp_patient_read_works",
                                  "heap-ppac-userType/webapp_unauth_doctor_routine_fails",
                                  "heap-ppac-userType/webapp_patient_info_leak_fails",
                                  "userType/webapp_double_usr_set",
                                  "password/webapp_password_leak",
                                  "bitcount",
                                  "rhealstone"
                                 ]
                                 )]


class bare(AllTests):
    tests = [test for test in AllTests.tests
                      if not any(test in s for s in
                                 ["ping_pong_works_1"
                                 ]
                                 )]


class Mibench(AllTests):
    tests = [
        "adpcm_decode",
        "adpcm_encode",
        "aes",
        "bitcount",
        "crc",
        "fft",
        "limits",
        "qsort",
        "randmath",
        "rc4",
    ]

class MibenchFrtos(Mibench):
    tests = [test for test in Mibench.tests
                      if not any(test in s for s in
                                 ["bitcount",
                                 ]
                                 )]

class stock_frtos(AllTests):
    tests = frtos.tests

class stock_bare(AllTests):
    tests = bare.tests


test_groups = {'all' : AllTests,
               'frtos' : frtos,
               'bare' : bare,
               'webapp' : webapp,
<<<<<<< variant A
               'mibench' : Mibench,
               'mibenchfrtos' : MibenchFrtos,
               'stock_frtos' : stock_frtos,
               'stock_bare' : stock_bare
>>>>>>> variant B
               'rhealstone_group' : rhealstone
======= end
}
