#include <stdio.h>

#include "test.h"

uint32_t t_instret(){
  uint64_t instret;
  asm volatile ("csrr %0, 0xb02 " : "=r"(instret));
  return instret;
}

int isp_main(int argc, char *argv[])
{
  t_printf("Running on RV%dV\n", __riscv_xlen); //read_mxl());
  test_main();
  return 0;
}
