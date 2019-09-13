#include "test_status.h"
#include "test.h"

extern unsigned short ult ( unsigned short a, unsigned short b);
extern unsigned short slt ( short a, short b);

extern unsigned short ulte ( unsigned short a, unsigned short b);
extern unsigned short slte ( short a, short b);

extern unsigned short ugt ( unsigned short a, unsigned short b);
extern unsigned short sgt ( short a, short b);

extern unsigned short ugte ( unsigned short a, unsigned short b);
extern unsigned short sgte ( short a, short b);


int test_main(void)
{
    unsigned short ra;
    short sa;

    test_positive();
    test_begin();
    test_start_timer();

    for(ra=0;;ra++) if(ult(ra,7)==0) break;
    if(ra!=7) test_fail();

    for(ra=0xF000;;ra++) if(ult(ra,0xF007)==0) break;
    if(ra!=0xF007) test_fail();

    for(sa=-7;;sa++) if(slt(sa,7)==0) break;
    if(sa!=7) test_fail();

    for(sa=-17;;sa++) if(slt(sa,-7)==0) break;
    if(sa!=-7) test_fail();

    for(ra=0;;ra++) if(ulte(ra,7)==0) break;
    if(ra!=8) test_fail();

    for(ra=0xF000;;ra++) if(ulte(ra,0xF007)==0) break;
    if(ra!=0xF008) test_fail();

    for(ra=0xF000;;ra++) if(ulte(ra,7)==0) break;
    if(ra!=0xF000) test_fail();

    for(sa=-7;;sa++) if(slte(sa,7)==0) break;
    if(sa!=8) test_fail();

    for(sa=-17;;sa++) if(slte(sa,-7)==0) break;
    if(sa!=-6) test_fail();

    for(ra=0;;ra++) if(ugt(ra,7)) break;
    if(ra!=8) test_fail();

    for(ra=0xF000;;ra++) if(ugt(ra,0xF007)) break;
    if(ra!=0xF008) test_fail();

    for(ra=0;;ra++) if(ugte(ra,7)) break;
    if(ra!=7) test_fail();

    for(ra=0xF000;;ra++) if(ugte(ra,0xF007)) break;
    if(ra!=0xF007) test_fail();

    test_print_total_time();
    return test_done();
}
