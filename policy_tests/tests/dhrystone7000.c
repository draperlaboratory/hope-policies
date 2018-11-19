/***** hpda:net.sources / homxb!gemini /  1:58 am  Apr  1, 1986*/
/*	EVERBODY:	Please read "APOLOGY" below. -rick 01/06/85
 *			See introduction in net.arch, or net.micro
 *
 *	"DHRYSTONE" Benchmark Program
 *
 *	Version:	C/1.1, 12/01/84
 *
 *	Date:		PROGRAM updated 01/06/86, RESULTS updated 03/31/86
 *
 *	Author:		Reinhold P. Weicker,  CACM Vol 27, No 10, 10/84 pg. 1013
 *			Translated from ADA by Rick Richardson
 *			Every method to preserve ADA-likeness has been used,
 *			at the expense of C-ness.
 *
 *	Compile:	cc -O dry.c -o drynr			: No registers
 *			cc -O -DREG=register dry.c -o dryr	: Registers
 *
 *	Defines:	Defines are provided for old C compiler's
 *			which don't have enums, and can't assign structures.
 *			The time(2) function is library dependant; Most
 *			return the time in seconds, but beware of some, like
 *			Aztec C, which return other units.
 *			The LOOPS define is initially set for 50000 loops.
 *			If you have a machine with large integers and is
 *			very fast, please change this number to 500000 to
 *			get better accuracy.  Please select the way to
 *			measure the execution time using the TIME define.
 *			For single user machines, time(2) is adequate. For
 *			multi-user machines where you cannot get single-user
 *			access, use the times(2) function.  If you have
 *			neither, use a stopwatch in the dead of night.
 *			Use a "printf" at the point marked "start timer"
 *			to begin your timings. DO NOT use the UNIX "time(1)"
 *			command, as this will measure the total time to
 *			run this program, which will (erroneously) include
 *			the time to malloc(3) storage and to compute the
 *			time it takes to do nothing.
 */

#include <sys/param.h>
#include <sys/types.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

// Headers for test framework
#include <time.h>
#include <sys/time.h>
#include <sys/times.h>
#include "test_status.h"
#include "test.h"
#include "mem.h"

#define MYPRINT(...) \
	do { \
		char sbuf[2048] = {0}; \
		snprintf(sbuf, 2048, __VA_ARGS__); \
		t_printf(sbuf); \
	} while(0)

/* Accuracy of timings and human fatigue controlled by next two lines */
#define LOOPS	50000		/* Use this for slow or 16 bit machines */

#define US_IN_SEC 1000000
#define	structassign(d, s)	d = s
typedef enum	{Ident1, Ident2, Ident3, Ident4, Ident5} Enumeration;

typedef int	OneToThirty;
typedef int	OneToFifty;
typedef char	CapitalLetter;
typedef char	String30[31];
typedef int	Array1Dim[51];
typedef int	Array2Dim[51][51];

struct	Record
{
	struct Record		*PtrComp;
	Enumeration		Discr;
	Enumeration		EnumComp;
	OneToFifty		IntComp;
	String30		StringComp;
};

typedef struct Record 	RecordType;
typedef RecordType *	RecordPtr;
typedef int		boolean;

#ifndef NULL
#define	NULL		0
#endif
#define	TRUE		1
#define	FALSE		0

#ifndef REG
#define	REG
#endif

int test_main(void);
void dhry_proc0(void);
void Proc1(REG RecordPtr PtrParIn);
void Proc2(OneToFifty *IntParIO);
void Proc3(RecordPtr *PtrParOut);
void Proc4(void);
void Proc5(void);
void Proc6(REG Enumeration EnumParIn, REG Enumeration *EnumParOut);
void Proc7(OneToFifty IntParI1, OneToFifty IntParI2, OneToFifty *IntParOut);
void Proc8(Array1Dim Array1Par, Array2Dim Array2Par, OneToFifty IntParI1, OneToFifty IntParI2);
boolean Func3(REG Enumeration EnumParIn);
boolean Func2(String30 StrParI1, String30 StrParI2);
Enumeration Func1(CapitalLetter CharPar1, CapitalLetter  CharPar2);


/*
 * Package 1
 */
int		IntGlob;
boolean		BoolGlob;
char		Char1Glob;
char		Char2Glob;
Array1Dim	Array1Glob;
Array2Dim	Array2Glob;
RecordPtr	PtrGlb;
RecordPtr	PtrGlbNext;

static uint8_t malloc_pool[4096];
static uint64_t malloc_offset = 0;
static void* malloc(uint64_t size)
{
	void* ptr = malloc_pool + malloc_offset;
	malloc_offset += size;
	return ptr;
}



Enumeration Func1(CapitalLetter CharPar1, CapitalLetter CharPar2)
{
	REG CapitalLetter	CharLoc1;
	REG CapitalLetter	CharLoc2;

	CharLoc1 = CharPar1;
	CharLoc2 = CharLoc1;
	if (CharLoc2 != CharPar2)
		return (Ident1);
	else
		return (Ident2);
}

boolean Func2(String30 StrParI1, String30 StrParI2)
{
	REG OneToThirty		IntLoc;
	REG CapitalLetter	CharLoc;

	IntLoc = 1;
	while (IntLoc <= 1)
		if (Func1(StrParI1[IntLoc], StrParI2[IntLoc+1]) == Ident1)
		{
			CharLoc = 'A';
			++IntLoc;
		}
	if (CharLoc >= 'W' && CharLoc <= 'Z')
		IntLoc = 7;
	if (CharLoc == 'X')
		return(TRUE);
	else
	{
		if (strcmp(StrParI1, StrParI2) > 0)
		{
			IntLoc += 7;
			return (TRUE);
		}
		else
			return (FALSE);
	}
}

boolean Func3(REG Enumeration EnumParIn)
{
	REG Enumeration	EnumLoc;

	EnumLoc = EnumParIn;
	if (EnumLoc == Ident3) return (TRUE);
	return (FALSE);
}


void Proc8(Array1Dim Array1Par, Array2Dim Array2Par, OneToFifty IntParI1, OneToFifty IntParI2)
{
	REG OneToFifty	IntLoc;
	REG OneToFifty	IntIndex;

	IntLoc = IntParI1 + 5;
	Array1Par[IntLoc] = IntParI2;
	Array1Par[IntLoc+1] = Array1Par[IntLoc];
	Array1Par[IntLoc+30] = IntLoc;
	for (IntIndex = IntLoc; IntIndex <= (IntLoc+1); ++IntIndex)
		Array2Par[IntLoc][IntIndex] = IntLoc;
	++Array2Par[IntLoc][IntLoc-1];
	Array2Par[IntLoc+20][IntLoc] = Array1Par[IntLoc];
	IntGlob = 5;
}

void Proc7(OneToFifty IntParI1, OneToFifty IntParI2, OneToFifty *IntParOut)
{
	REG OneToFifty	IntLoc;

	IntLoc = IntParI1 + 2;
	*IntParOut = IntParI2 + IntLoc;
}


void Proc6(REG Enumeration EnumParIn, REG Enumeration *EnumParOut)
{
	*EnumParOut = EnumParIn;
	if (! Func3(EnumParIn) )
		*EnumParOut = Ident4;
	switch (EnumParIn)
	{
	case Ident1:	*EnumParOut = Ident1; break;
	case Ident2:	if (IntGlob > 100) *EnumParOut = Ident1;
			else *EnumParOut = Ident4;
			break;
	case Ident3:	*EnumParOut = Ident2; break;
	case Ident4:	break;
	case Ident5:	*EnumParOut = Ident3;
	}
}
void Proc5(void)
{
	Char1Glob = 'A';
	BoolGlob = FALSE;
}



void Proc4(void)
{
	REG boolean	BoolLoc;

	BoolLoc = Char1Glob == 'A';
	BoolLoc |= BoolGlob;
	Char2Glob = 'B';
}


void Proc3(RecordPtr *PtrParOut)
{
	if (PtrGlb != NULL)
		*PtrParOut = PtrGlb->PtrComp;
	else
		IntGlob = 100;
	Proc7(10, IntGlob, &PtrGlb->IntComp);
}

void Proc2(OneToFifty *IntParIO)
{
	REG OneToFifty		IntLoc;
	REG Enumeration		EnumLoc;

	IntLoc = *IntParIO + 10;
	for(;;)
	{
		if (Char1Glob == 'A')
		{
			--IntLoc;
			*IntParIO = IntLoc - IntGlob;
			EnumLoc = Ident1;
		}
		if (EnumLoc == Ident1)
			break;
	}
}

void Proc1(REG RecordPtr PtrParIn)
{
#define	NextRecord	(*(PtrParIn->PtrComp))

	structassign(NextRecord, *PtrGlb);
	PtrParIn->IntComp = 5;
	NextRecord.IntComp = PtrParIn->IntComp;
	NextRecord.PtrComp = PtrParIn->PtrComp;
	Proc3(&NextRecord.PtrComp);
	if (NextRecord.Discr == Ident1)
	{
		NextRecord.IntComp = 6;
		Proc6(PtrParIn->EnumComp, &NextRecord.EnumComp);
		NextRecord.PtrComp = PtrGlb->PtrComp;
		Proc7(NextRecord.IntComp, 10, &NextRecord.IntComp);
	}
	else
		structassign(*PtrParIn, NextRecord);

#undef	NextRecord
}

void dhry_proc0(void)
{
	OneToFifty		IntLoc1;
	REG OneToFifty		IntLoc2;
	OneToFifty		IntLoc3;
	REG char		CharIndex;
	Enumeration	 	EnumLoc;
	String30		String1Loc;
	String30		String2Loc;

	uint32_t		i;

	volatile uint32_t	starttime;
	volatile uint32_t	benchtime_us;
	uint32_t		nulltime;
	uint32_t		endtime;

	starttime = sys_GetWallTimestampUs();
	for (i = 0; i < LOOPS; ++i)
	{
		volatile asm("nop");
	}
	endtime = sys_GetWallTimestampUs();
	nulltime = endtime - starttime; /* Computes overhead of looping */

	PtrGlbNext = (RecordPtr)malloc(sizeof(RecordType));
	PtrGlb = (RecordPtr) malloc(sizeof(RecordType));
	PtrGlb->PtrComp = PtrGlbNext;
	PtrGlb->Discr = Ident1;
	PtrGlb->EnumComp = Ident3;
	PtrGlb->IntComp = 40;
	strcpy(PtrGlb->StringComp, "DHRYSTONE PROGRAM, SOME STRING");

	/* Was missing in published program */
	Array2Glob[8][7] = 10;

	/*****************
	-- Start Timer --
	*****************/
	starttime = sys_GetWallTimestampUs();
	for (i = 0; i < LOOPS; ++i)
	{

		Proc5();
		Proc4();
		IntLoc1 = 2;
		IntLoc2 = 3;
		strcpy(String2Loc, "DHRYSTONE PROGRAM, 2'ND STRING");
		EnumLoc = Ident2;
		BoolGlob = ! Func2(String1Loc, String2Loc);
		while (IntLoc1 < IntLoc2)
		{
			IntLoc3 = 5 * IntLoc1 - IntLoc2;
			Proc7(IntLoc1, IntLoc2, &IntLoc3);
			++IntLoc1;
		}
		Proc8(Array1Glob, Array2Glob, IntLoc1, IntLoc3);
		Proc1(PtrGlb);
		for (CharIndex = 'A'; CharIndex <= Char2Glob; ++CharIndex)
			if (EnumLoc == Func1(CharIndex, 'C'))
				Proc6(Ident1, &EnumLoc);
		IntLoc3 = IntLoc2 * IntLoc1;
		IntLoc2 = IntLoc3 / IntLoc1;
		IntLoc2 = 7 * (IntLoc3 - IntLoc2) - IntLoc1;
		Proc2(&IntLoc1);
	}
	benchtime_us = sys_GetWallTimestampUs() - starttime - nulltime;
	MYPRINT("Dhrystone(%s) time for %ld passes = %ld\n",
		Version,
		(long) LOOPS, benchtime_us/US_IN_SEC);
	MYPRINT("This machine benchmarks at %ld dhrystones/second\n",
		((long) LOOPS)) / (benchtime/US_IN_SEC);
}

int test_main (void)
{
	test_positive();
	test_begin();

	dhry_proc0();

	test_pass();
	return test_done();
}
/* ---------- */
