/* testd - Test adpcm decoder */

#include "adpcm.h"
#include <stdio.h>
#include "input.h"

#include "test_status.h"
#include "test.h"

#define NSAMPLES 1000
#define NINC  (NSAMPLES / 2)

short	sbuf[NSAMPLES];

int test_main() {
    test_positive();
    test_begin();
    test_start_timer();

    struct adpcm_state state = {};
    int n = 0;
    const unsigned char * currentN = test_data;
    int maxN = sizeof(test_data);
    
    t_printf("Initial valprev=%d, index=%d\n", state.valprev, state.index);
    
    while(1) {
        int bytesIntoRead = ((unsigned int)currentN) - ((unsigned int)test_data);
        int testN = bytesIntoRead + NINC;
        n = (testN <= maxN) ? NINC : maxN - bytesIntoRead;

        if ( n == 0 ) break;

        adpcm_decoder(currentN, sbuf, n*2, &state);
        currentN = test_data + bytesIntoRead + n;
    }
    
    t_printf("Final valprev=%d, index=%d\n", state.valprev, state.index);

    test_print_total_time();
    return test_done();
}
