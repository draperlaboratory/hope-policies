#include "test_status.h"
#include "test.h"

extern unsigned int abcmath ( void );

int test_main ( void )
{
    test_positive();
    test_begin();
    test_start_timer();

    t_printf("abcmath result: %u\n", abcmath());

    test_print_total_time();
    return test_done();
}
