/**********************************************************************
 *
 * Filename:    main.c
 * 
 * Description: A simple test program for the CRC implementations.
 *
 * Notes:       To test a different CRC standard, modify crc.h.
 *
 * 
 * Copyright (c) 2000 by Michael Barr.  This software is placed into
 * the public domain and may be used for any purpose.  However, this
 * notice must not be changed or removed and no warranty is either
 * expressed or implied by its publication or distribution.
 **********************************************************************/
#include <stdio.h>
#include <string.h>

#include "crc.h"

#include "test_status.h"
#include "test.h"

int test_main(void)
{
	unsigned char  test[] = "123456789";
	crc result;

	test_positive();
	test_begin();
	test_start_timer();

	/*
	 * Print the check value for the selected CRC algorithm.
	 */
	t_printf("The check value for the %s standard is 0x%X\n", CRC_NAME, CHECK_VALUE);
	
	/*
	 * Compute the CRC of the test message, slowly.
	 */
	result = crcSlow(test, strlen(test));
	t_printf("The crcSlow() of \"123456789\" is 0x%X\n", result);
	if (result != CHECK_VALUE)
	{
		test_error("Incorrect crcSlow result\n");
	}
	
	/*
	 * Compute the CRC of the test message, more efficiently.
	 */
	crcInit();
	result = crcFast(test, strlen(test));
	t_printf("The crcFast() of \"123456789\" is 0x%X\n", result);
	if (result != CHECK_VALUE)
	{
		test_error("Incorrect crcFast result\n");
	}

	test_print_total_time();
	return test_done();
}   /* main() */
