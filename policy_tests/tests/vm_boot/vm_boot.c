#include <stdint.h>
#include <unistd.h>

void vm_test(void)
{
  test_positive(); // identify test as positive (will complete)
  printf("test\n");
  exit(0);
}

int test_main(void)
{
  vm_boot((uintptr_t)vm_test);

  test_pass();
  return test_done();
}