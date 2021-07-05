#include <unistd.h>

#include "test_status.h"
#include "test.h"

int test_main(void)
{
	test_positive();

    volatile uint64_t* brk = sbrk(sizeof(uint64_t));
    *brk = 0;

	test_pass();
	return test_done();
}