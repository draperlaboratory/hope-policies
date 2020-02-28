/*
 * Copyright © 2020 The Charles Stark Draper Laboratory, Inc. and/or Dover Microsystems, Inc.
 * All rights reserved. 
 *
 * Use and disclosure subject to the following license. 
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 * 
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#include "test_status.h"
#include "test.h"

static int read_mxl_inasm(void){
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

/*
 * Test to check that inline assembly with branches does not cause and
 * error.
 */
int test_main(void)
{
   test_positive();
   test_begin();

   t_printf("Still Running on RV%dV\n", read_mxl_inasm());

   return test_done();
}

