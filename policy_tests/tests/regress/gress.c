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
void print_binary ( unsigned int x, unsigned int digits )
{
    unsigned int bit;
    t_printf("0b");
    for (bit = 1 << (digits - 1); bit; bit >>= 1) {
        t_printf((bit & x) ? "1" : "0");
    }
    t_printf("\n");
}
//------------------------------------------------------------------------
int test_main ( void )
{
    unsigned int rb;
    unsigned int rc;
    unsigned int prand;
    unsigned int sum;
    unsigned int shift[6] = {0,1,2,31,32,33};
    unsigned int ror_flags[6] = {0b100,0b101,0b000,0b000,0b101,0b101};
    unsigned int lsr_flags[6] = {0b100,0b001,0b000,0b000,0b011,0b010};
    unsigned int lsl_flags[6] = {0b100,0b001,0b100,0b100,0b011,0b010};

    test_positive();
    test_begin();
    test_start_timer();

    prand=0xa0000005;
    for(rb=0;rb<6;rb++)
    {
        rc=ROR_FLAG(prand,shift[rb]);
        if(rc != ror_flags[rb]) test_error("Incorrect ROR flags\n");
        rc=LSR_FLAG(prand,shift[rb]);
        if(rc != lsr_flags[rb]) test_error("Incorrect LSR flags\n");
        rc=LSL_FLAG(prand,shift[rb]);
        if(rc != lsl_flags[rb]) test_error("Incorrect LSL flags\n");
    }

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

