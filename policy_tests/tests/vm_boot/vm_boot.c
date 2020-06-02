#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "test_status.h"
#include "vm.h"

void vm_test(void)
{
  test_positive(); // identify test as positive (will complete)
  printf("test\n");
  test_pass();
  exit(test_done());
}

int test_main(void)
{
  vm_boot((uintptr_t)vm_test);
  return 0;
}