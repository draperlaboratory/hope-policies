#include <stdio.h>
#include <stdlib.h>

#include "test_status.h"

__attribute__((noinline))
void func1(void){
  t_printf("function 1\n");
}

__attribute__((noinline))
void func2(void){
  t_printf("function 2\n");
}

__attribute__((noinline))
void sneaky(void *ptr){
  memset(ptr, 0x0, 4);
}

int isp_main(void){
  test_negative(); // identify test as negative (will fail to complete due to policy violation)
  test_begin();

  void (*fptr)();
  srand(0);
  if(rand() % 2 == 0) fptr = func1;
  else fptr = func2;

  sneaky(&fptr);

  fptr();

  return test_done();
}
