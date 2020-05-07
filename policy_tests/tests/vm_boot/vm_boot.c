#include <stdint.h>

void vm_test(void)
{
  exit(0);
}

int test_main(void)
{
  test_positive(); // identify test as positive (will complete)

  vm_boot((uintptr_t)vm_test);

  test_pass();
  return test_done();
}