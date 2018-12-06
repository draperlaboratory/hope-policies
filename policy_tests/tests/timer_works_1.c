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

// include malloc wrappers
#include "mem.h"

#define INST_COUNT 100000

extern uint32_t get_usec_time();
extern uint32_t get_inst_ret();
/*
 * Test to calibrate cpu and timer frequency
 * 
 */
int isp_main(void)
  {
    test_positive(); // identify test as positive (will complete)
    uint32_t inst_ret = 0;
    uint32_t last_ret = 0;
    uint32_t inst_count = 0;
    uint32_t start_time = 0;
    uint32_t end_time = 0;

    start_time = get_usec_time();
    last_ret = get_inst_ret();
    while(inst_count < INST_COUNT){
      inst_ret = get_inst_ret();
      inst_count += inst_ret - last_ret;
      last_ret = inst_ret;
        
    }
    end_time = get_usec_time();

    t_printf("Test Complete\n");
    t_printf("Executed %d instructions\n", inst_count);
    t_printf("Elapsed %d usec\n", end_time - start_time);
    
    test_pass();
    return test_done();
  }

