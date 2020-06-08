#include <stdio.h>

#include "test.h"

uint32_t t_instret(){
  uint64_t instret;
  asm volatile ("csrr %0, 0xb02 " : "=r"(instret));
  return instret;
}

int isp_main(int argc, char *argv[])
{
  t_printf("Running on RV%d\n", __riscv_xlen);
  test_main();
  return 0;
}
