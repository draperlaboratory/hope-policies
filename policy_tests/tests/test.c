#include <stdio.h>

#include "test.h"

uint32_t t_instret(){
  uint64_t instret;
  asm volatile ("csrr %0, 0xb02 " : "=r"(instret));
  return instret;
}

static int read_mxl(void){
  long mxl;
  long misa;
  asm("csrr %0, 0x301\n"
      "bgez %0, rv32\n"
      "slli %0, %0, 1\n"
      "bgez %0, rv64\n"
      "li   %1, 128\n"
      "j rv_out\n"
      "rv32: li   %1, 32\n"
      "j rv_out\n"
      "rv64: li   %1, 64\n"
      "rv_out: li %0, 0"
      : "=r"(misa), "=r"(mxl) : );
  return mxl;
}

int isp_main(int argc, char *argv[])
{
  t_printf("Running on RV%dV\n", read_mxl());
  test_main();
  return 0;
}
