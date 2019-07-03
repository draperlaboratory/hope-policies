/*
 * Test status functions
 */

#ifndef TEST_STATUS_H
#define TEST_STATUS_H

// Identify positive case (test will end)
void test_positive(void);

// Identify negative case (test will never end)
void test_negative(void);

// Set passing status at start of test
void test_begin(void);

// Start a timer for benchmark tests
void test_start_timer(void);

// Print the current time interval
void test_print_time_interval(void);

// Print the total time elapsed since test_start_timer() call
void test_print_total_time(void);

// Set passing status
void test_pass(void);

// Set failing status
void test_fail(void);

// Output message and set failing
void test_error(const char *fmt, ...);

// print the test status for positive test case
int  test_done(void);

// print the test status for negative test case
int  test_done_pump(void);

#endif // TEST_STATUS_H
