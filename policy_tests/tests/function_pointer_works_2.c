#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
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

int test_main(void){
  test_positive(); // identify test as positive (will complete)
  test_begin();

  volatile void (*fptr)();
  srand(0);
  if(rand() % 2 == 0) fptr = func1;
  else fptr = func2;

  fptr();

  return test_done();
}
