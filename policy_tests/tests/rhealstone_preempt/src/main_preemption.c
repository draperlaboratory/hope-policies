/****************************************************************************/
/* Author: Jesse Millwood                                                   */
/* Date: 4/25/19                                                            */
/* Preemption Time Benchmark                                                */
/* OS: FreeRTOS                                                             */
/* Plaform: RISC-V SiFIVE QEMU 3.14 Model                                   */
/* Comments:                                                                */
/* This is a mix between Timohty Boger's Master's Thesis Implementation for */
/* the ZC702 and Daniel Ramirez's RTEMS implementation                      */
/****************************************************************************/

#include "FreeRTOS.h"
#include "rhealstone_utils.h"
#include "task.h"
#include "queue.h"
#include "timers.h"
#include "stdio.h"

// Priorities at which the tasks are created
#define mainFIRST_TASK_PRIORITY ( tskIDLE_PRIORITY + 4)
#define mainSECOND_TASK_PRIORITY ( tskIDLE_PRIORITY + 5 )
#define mainTHIRD_TASK_PRIORITY ( tskIDLE_PRIORITY + 3 )    // Highest
//*********************************************************
//Associate Functions with Tasks
static void prvFirst( void *pvParameters );
static void prvSecond( void *pvParameters );
static void prvReport( void *pvParameters );
//*********************************************************
//Task and Queue Handles
xTaskHandle xHandleFirst;
xTaskHandle xHandleSecond;
xTaskHandle xHandleReport;
extern xTaskHandle xIspTask;
//*********************************************************

// #define BENCHMARK_LOOPS 50000
#define BENCHMARK_LOOPS 100

uint32_t count1;
uint32_t count2;
uint32_t i;
mTaskSwitchTickRecord_t test_record;

//Main
int test_main ( void )
{
    vTaskPrioritySet(&xIspTask, tskIDLE_PRIORITY + 3);
    test_positive();
    test_begin();

    vTaskSuspendAll();
    test_record.baseline_begin_ticks = get_timer_value();
    for (count1 = 0; count1 < (BENCHMARK_LOOPS * 2) - 1; count1++)
    {
        // Do Nothing
    }
    test_record.baseline_end_ticks = get_timer_value();


    xTaskCreate( prvFirst, "Task 1", configMINIMAL_STACK_SIZE, NULL, mainFIRST_TASK_PRIORITY, &xHandleFirst );
    xTaskCreate( prvSecond, "Task 2", configMINIMAL_STACK_SIZE, NULL, mainSECOND_TASK_PRIORITY, &xHandleSecond );
    xTaskCreate( prvReport, "Report", configMINIMAL_STACK_SIZE, NULL, mainTHIRD_TASK_PRIORITY, &xHandleReport );
    vTaskSuspend( xHandleSecond );
    vTaskSuspend( xHandleReport);
    xTaskResumeAll();

}


static void prvReport (void *pvParameters)
{
    uint32_t work_baseline_ticks;
    uint32_t work_measured_ticks;
    uint32_t measured_ticks;
    uint32_t measured_time_usecs;
    uint32_t timer_freq;

    vTaskDelete(xHandleFirst);
    vTaskDelete(xHandleSecond);

    work_measured_ticks = test_record.measured_work_end_ticks - test_record.measured_work_begin_ticks;
    work_baseline_ticks = test_record.baseline_end_ticks - test_record.baseline_begin_ticks;
    if (work_baseline_ticks > work_measured_ticks)
    {
        printf("ERROR: Ticks taken for baseline serial work is more than when running test\n");
        printf("       The baseline should be less\n");
        printf(" Baseline  : %lu\n", work_baseline_ticks);
        printf(" Test      : %lu\n", work_measured_ticks);
    }
    else
    {
        timer_freq = get_timer_freq();
        measured_ticks = (work_measured_ticks - work_baseline_ticks)/BENCHMARK_LOOPS;
        measured_time_usecs = ticks_to_usecs(measured_ticks);
        print_results_json("preemtion", "base", measured_ticks, timer_freq, measured_time_usecs);
    }
    vTaskResume(xIspTask);
    test_pass();
    test_done();
}

static void prvSecond (void *pvParameters)
{

    for ( ; count1 < BENCHMARK_LOOPS -1 ;)
    {
        vTaskSuspend( xHandleSecond );
    }
    test_record.measured_work_end_ticks = get_timer_value();
    vTaskSuspend( xHandleFirst );
    vTaskResume( xHandleReport);
    vTaskSuspend( xHandleSecond);

}

static void prvFirst (void *pvParameters)
{
    vTaskSuspend( xIspTask );
    test_record.measured_work_begin_ticks = get_timer_value();
    for (count1 = 0; count1 < BENCHMARK_LOOPS; count1++)
    {
        vTaskResume(xHandleSecond); // Should cause preemption here
    }

}
