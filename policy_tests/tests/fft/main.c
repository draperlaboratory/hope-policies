#include <stdlib.h>
#include <math.h>
#include "fourier.h"

#include "test_status.h"
#include "test.h"

int invfft=0;
unsigned MAXSIZE; // small 4096, 8192 inverse, 512 for memory-limited systems
unsigned MAXWAVES=4; //large has 8

#ifndef ARRAYSIZE
#define ARRAYSIZE 1024
#endif

static float realin[ARRAYSIZE];
static float imagin[ARRAYSIZE];
static float realout[ARRAYSIZE];
static float imagout[ARRAYSIZE];
static float Coeff[16];
static float Amp[16];

int old_main();
    
// main for benchmark purposes that does fft and inverse fft
int test_main() {
    test_positive();
    test_begin();
    test_start_timer();

    MAXSIZE = ARRAYSIZE / 2;
    old_main();
    invfft = 1;
    MAXSIZE = ARRAYSIZE;
    old_main();

    test_print_total_time();
    return test_done();
}

int old_main() {
	unsigned i,j;
	float *RealIn;
	float *ImagIn;
	float *RealOut;
	float *ImagOut;
	float *coeff;
	float *amp;

		
 srand(1);

/* RealIn=(float*)malloc(sizeof(float)*MAXSIZE);
 ImagIn=(float*)malloc(sizeof(float)*MAXSIZE);
 RealOut=(float*)malloc(sizeof(float)*MAXSIZE);
 ImagOut=(float*)malloc(sizeof(float)*MAXSIZE);
 coeff=(float*)malloc(sizeof(float)*MAXWAVES);
 amp=(float*)malloc(sizeof(float)*MAXWAVES);
*/

 //Statically allocate
	RealIn = realin;
	ImagIn = imagin;
	RealOut = realout;
	ImagOut = imagout;
	coeff = Coeff;
	amp = Amp;

 /* Makes MAXWAVES waves of random amplitude and period */
	for(i=0;i<MAXWAVES;i++) 
	{
		coeff[i] = rand()%1000;
		amp[i] = rand()%1000;
	}
 for(i=0;i<MAXSIZE;i++) 
 {
   /*   RealIn[i]=rand();*/
	 RealIn[i]=0;
	 for(j=0;j<MAXWAVES;j++) 
	 {
		 /* randomly select sin or cos */
		 if (rand()%2)
		 {
		 		RealIn[i]+=coeff[j]*cos(amp[j]*i);
			}
		 else
		 {
		 	RealIn[i]+=coeff[j]*sin(amp[j]*i);
		 }
  	 ImagIn[i]=0;
	 }
 }

 /* regular*/
 fft_float (MAXSIZE,invfft,RealIn,ImagIn,RealOut,ImagOut);
 
 t_printf("RealOut:\n");
 for (i=0;i<MAXSIZE;i++)
   t_printf("%f \t", RealOut[i]);
 t_printf("\n");

t_printf("ImagOut:\n");
 for (i=0;i<MAXSIZE;i++)
   t_printf("%f \t", ImagOut[i]);
   t_printf("\n");

/* free(RealIn);
 free(ImagIn);
 free(RealOut);
 free(ImagOut);
 free(coeff);
 free(amp);
*/ return 0;


}
