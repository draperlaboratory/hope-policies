/*
 * Test status functions
 */

#ifndef TEST_STATUS_H
#define TEST_STATUS_H

// Identify positive case (test will end)
void test_positive();

// Identify negative case (test will never end)
void test_negative();

// Set passing status at start of test
void test_begin();

// Set passing status
void test_pass();

// Set failing status
void test_fail();

// Output message and set failing
void test_error(const char *fmt, ...);

// print the test status for positive test case
int  test_done();

// print the test status for negative test case
int  test_done_pump();

#endif // TEST_STATUS_H
