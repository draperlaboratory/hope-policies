#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#include "test_status.h"
#include "test.h"


int test_main(void)
  {
    double x;

    test_positive(); // identify test as positive (will complete)

    x = 10.0;
    t_printf("x is %f\n", x);

    test_pass();
    return test_done();
  }

