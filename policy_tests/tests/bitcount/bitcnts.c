/* +++Date last modified: 05-Jul-1997 */

/*
**  BITCNTS.C - Test program for bit counting functions
**
**  public domain by Bob Stout & Auke Reitsma
*/

#include <stdlib.h>
#include "conio.h"
#include <limits.h>
#include "bitops.h"

extern uint32_t uiPortGetWallTimestampUs(void);

#define US_PER_SEC 1000000

#include "test_status.h"
#include "test.h"

#define FUNCS  7

static int CDECL bit_shifter(long int x);

int test_main(void)
{
  uint32_t start, stop;
  uint32_t ct, cmin = LONG_MAX, cmax = 0, ct_sec, ct_frac;
  int i, cminix, cmaxix;
  long j, n, seed;
  // Reduced iterations from 1152000 to
  // run within test framework time limit
  int iterations=100;
  static int (* CDECL pBitCntFunc[FUNCS])(long) = {
    bit_count,
    bitcount,
    ntbl_bitcnt,
    ntbl_bitcount,
    /*            btbl_bitcnt, DOESNT WORK*/
    BW_btbl_bitcount,
    AR_btbl_bitcount,
    bit_shifter
  };
  static char *text[FUNCS] = {
    "Optimized 1 bit/loop counter",
    "Ratko's mystery algorithm",
    "Recursive bit count by nybbles",
    "Non-recursive bit count by nybbles",
    /*            "Recursive bit count by bytes",*/
    "Non-recursive bit count by bytes (BW)",
    "Non-recursive bit count by bytes (AR)",
    "Shift and count bits"
  };

  test_positive();
  test_begin();
  test_start_timer();
  
  t_printf("Bit counter algorithm benchmark\n");
  
  for (i = 0; i < FUNCS; i++) {
    start = uiPortGetWallTimestampUs();
    
    for (j = n = 0, seed = rand(); j < iterations; j++, seed += 13)
	 n += pBitCntFunc[i](seed);
    
    stop = uiPortGetWallTimestampUs();
    ct = (stop - start);
    if (ct < cmin) {
	 cmin = ct;
	 cminix = i;
    }
    if (ct > cmax) {
	 cmax = ct;
	 cmaxix = i;
    }
    
    ct_sec = ct / US_PER_SEC;
    ct_frac = ct % US_PER_SEC;

    t_printf("%-38s> Time: %d.%06d s.; Bits: %ld\n", text[i], ct_sec, ct_frac, n);
  }
  t_printf("\nBest  > %s\n", text[cminix]);
  t_printf("Worst > %s\n", text[cmaxix]);

  test_print_total_time();
  return test_done();
}

static int CDECL bit_shifter(long int x)
{
  int i, n;
  
  for (i = n = 0; x && (i < (sizeof(long) * CHAR_BIT)); ++i, x >>= 1)
    n += (int)(x & 1L);
  return n;
}
