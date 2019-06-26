/* testc - Test adpcm coder */

#include "adpcm.h"
#include <stdio.h>
#include "input.h"

#include "test_status.h"
#include "test.h"

// Fraction of the input.h array to be included
// 1 includes the whole array
// A higher number means a smaller input
#ifndef INPUT_FRAC
#define INPUT_FRAC 1
#endif

#define NSAMPLES 1000
#define NINC  (NSAMPLES * 2)

char	abuf[NSAMPLES/2];

int test_main() {
    test_positive();
    test_begin();
    test_start_timer();

    struct adpcm_state state = {};
    int n = 0;
    const unsigned char * currentN = test_data;
    int maxN = sizeof(test_data) / INPUT_FRAC;
    
    t_printf("Initial valprev=%d, index=%d\n", state.valprev, state.index);

    while(1) {
        int bytesIntoRead = ((unsigned int)currentN) - ((unsigned int)test_data);
        int testN = bytesIntoRead + NINC;
        n = (testN <= maxN) ? NINC : maxN - bytesIntoRead;

        if ( n == 0 ) break;
	
        adpcm_coder(currentN, abuf, n/2, &state);
        currentN = test_data + bytesIntoRead + n;
        //write(1, abuf, n/4);
    }
    
    t_printf("Final valprev=%d, index=%d\n", state.valprev, state.index);
    test_print_total_time();
    return test_done();
}
