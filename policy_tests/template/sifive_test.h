/*
 * SiFive Test Device
 */
#ifndef _SIFIVE_TEST_H_
#define _SIFIVE_TEST_H_

#define SIFIVE_TEST_ADDR 0x100000

#define SIFIVE_TEST_FAIL 0x3333
#define SIFIVE_TEST_PASS 0x5555

volatile uint32_t *test_device;

#endif
