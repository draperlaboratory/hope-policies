#include <stdio.h>

#include "test.h"

uint32_t t_instret(){
  uint64_t instret;
  asm volatile ("csrr %0, 0xb02 " : "=r"(instret));
  return instret;
}

static int read_mxl(void){
  long misa;
  asm("csrr %0, 0x301\n" : "=r"(misa) : );
  if (misa > 0)
      return 32;
  else
      return 64;
}

int isp_main(int argc, char *argv[])
{
  t_printf("Running on RV%dV\n", read_mxl());
  test_main();
  return 0;
}
