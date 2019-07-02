#ifndef RHEALSTONE_UTILS_H
#define RHEALSTONE_UTILS_H

#include "FreeRTOS.h"
#include "stdio.h"
// ISP Test Framework
#include "test_status.h"
#include "test.h"

typedef struct MEASURE_TASK_SWITCH_TICKS {
    uint32_t baseline_begin_ticks;
    uint32_t baseline_end_ticks;
    uint32_t measured_work_begin_ticks;
    uint32_t measured_work_end_ticks;
} mTaskSwitchTickRecord_t;

uint32_t ticks_to_usecs(uint32_t ticks);
void print_results_json(char* name, char* variant, uint32_t ticks, uint32_t timer_freq, uint32_t time_result_us);
int test_main(void);

#endif /* RHEALSTONE_UTILS_H */
