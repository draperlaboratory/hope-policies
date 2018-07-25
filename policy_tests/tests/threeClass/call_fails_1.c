
#include "test_status.h"
#include "test.h"

__attribtue__((noinline))
void target(void){
  t_printf("this is a target function\n");
  t_printf("canst thou hack it?\n");
  return;
}

int test_main(void){
  size_t addr = (size_t)target + t;
  void (*fptr)(void) = (void(*)(void))addr;
  test_negative();
  target();
  test_begin();
  fptr();
  return test_done();
}
