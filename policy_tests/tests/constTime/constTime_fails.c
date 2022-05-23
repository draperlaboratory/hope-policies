/*
 * Copyright © 2017-2018 The Charles Stark Draper Laboratory, Inc. and/or Dover Microsystems, Inc.
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


uint32_t modular_exponent(uint32_t a, uint32_t mod, uint8_t exp[4]) {
  uint32_t result = 1;
  uint32_t temp;

  for (int i = 3; i >= 0; i--) {
    for (int j = 7; j >= 0; j--) {
      result = ((uint64_t) result * result) % mod;
      temp   = ((uint64_t) a * result) % mod;
      result = (exp[i] & 1 << j) ? temp : result; // the ternary should cause a failure
    }
  }
  return result;
}

int test_main(void)
  {
    test_negative(); // identify test as positive (will complete)

    test_begin();
    
    uint8_t  secret[4] = {0xBA, 0x5E, 0xBA, 0x11}; // dedicated to Pedro Martinez
    uint32_t val       = 42;   // dummy val
    uint32_t mod       = 7757; // picked a prime with a lot of 7s
   
    uint32_t res = modular_exponent(val, mod, secret);
 
    test_fail();
    return test_done();
  }

