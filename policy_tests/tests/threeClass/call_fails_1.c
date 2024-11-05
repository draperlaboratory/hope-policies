
#include "test_status.h"
#include "test.h"

__attribute__((noinline)) void target(void){
  printf("this is a target function\n");
  printf("canst thou hack it?\n");
  return;
}

int test_main(void){
  volatile size_t addr = (size_t)target + 4;
  volatile void (*fptr)(void) = (void(*)(void))addr;
  test_negative();
  target();
  test_begin();
  fptr();
  return test_done();
}
