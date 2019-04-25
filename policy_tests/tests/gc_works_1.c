/*
 * Copyright © 2017-2018 The Charles Stark Draper Laboratory, Inc. and/or Dover
 * Microsystems, Inc. All rights reserved.
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

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "test.h"
#include "test_status.h"

// include malloc wrappers
#include "mem.h"

volatile void *old_ptr = NULL;
volatile void *old_ptr_copy = NULL;

static const size_t NUM_COLORS = 20;

#define SAVE_TO_REG(var) asm("mv t2, %0" : : "r"(var) : "t2")
#define LOAD_FROM_REG(var) asm("mv %0, t2" : "=r"(var)::)

int test_main(void) {
  test_positive(); // identify test as positive (will complete)
  test_begin();

  // Allocate a buffer with color X and immediately free it.
  // Try to save a copy of the pointer into a register.
  old_ptr = malloc(12);
  free(old_ptr);
  old_ptr_copy = old_ptr;
  SAVE_TO_REG(old_ptr_copy);

  // Burn through the rest of the colors, so that next time we allocate we get
  // the color X again.
  for (int allocs = 0; allocs < NUM_COLORS - 1; allocs++) {
    // Temporarily saves the registered copy into memory because free scans
    // registers.
    // Hope that memory scanning doesn't use this window to zero out the memory
    // copy.
    LOAD_FROM_REG(old_ptr_copy);
    free(malloc(12));
    SAVE_TO_REG(old_ptr_copy);
  }

  // Allocate a new buffer. The new buffer should also have the same color X.
  malloc(12);

  // Try to access the new buffer via the old pointer. This should fail.
  LOAD_FROM_REG(old_ptr_copy);
  uint32_t access = ((uint32_t *)old_ptr_copy)[0];
  t_printf("THIS SHOULD NOT HAVE BEEN PRINTED!!! %d\n", access);

  // Allocate a new buffer, which should occupy the same address as the old
  test_done();
}
