#include "test_status.h"
#include "test.h"

//------------------------------------------------------------------------
//------------------------------------------------------------------------
//void PUT32 ( unsigned int, unsigned int);

unsigned int ROR ( unsigned int rd, unsigned int rs );
unsigned int ROR_FLAG ( unsigned int rd, unsigned int rs );
unsigned int LSR ( unsigned int rd, unsigned int rs );
unsigned int LSR_FLAG ( unsigned int rd, unsigned int rs );
unsigned int LSL ( unsigned int rd, unsigned int rs );
unsigned int LSL_FLAG ( unsigned int rd, unsigned int rs );

//------------------------------------------------------------------------
unsigned int prand32 ( unsigned int x )
{
    if(x&1)
    {
        x=x>>1;
        x=x^0xBF9EC099;
    }
    else
    {
        x=x>>1;
    }
    return(x);
}
//------------------------------------------------------------------------
int test_main ( void )
{
    unsigned int rb;
    unsigned int rc;
    unsigned int prand;
    unsigned int sum;

    test_positive();
    test_begin();
    test_start_timer();

    prand=0x12345678;
    //for(rb=0;rb<5;rb++)
    //{
        //prand=prand32(prand);
        //hexstring(prand);
    //}
    sum=0;
    for(rb=0;rb<5000;rb++)
    {
        prand=prand32(prand);
        rc=ROR(prand,rb);
        //PUT32(0xD0000000,rc);
        //hexstring(rc);
        sum+=rc;
        rc=ROR_FLAG(prand,rb);
        sum+=rc;
    }
    for(rb=0;rb<5000;rb++)
    {
        prand=prand32(prand);
        rc=LSR(prand,rb);
        sum+=rc;
        rc=LSR_FLAG(prand,rb);
        sum+=rc;
    }
    for(rb=0;rb<5000;rb++)
    {
        prand=prand32(prand);
        rc=LSL(prand,rb);
        sum+=rc;
        rc=LSL_FLAG(prand,rb);
        sum+=rc;
    }

    t_printf("%x\r\n", sum);
    test_print_total_time();
    return test_done();
}
//------------------------------------------------------------------------
//------------------------------------------------------------------------

