#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "test_status.h"
#include "bsp/vm.h"

int test_main(void)
{
  test_positive(); // identify test as positive (will complete)
  printf("test\n");
  test_pass();
  return test_done();
}