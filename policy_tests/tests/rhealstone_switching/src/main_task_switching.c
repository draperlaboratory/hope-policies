/****************************************************************************/
/* Author: Jesse Millwood                                                   */
/* Date: 4/25/19                                                            */
/* Task Switching Benchmark                                                 */
/* OS: FreeRTOS                                                             */
/* Plaform: RISC-V SiFIVE QEMU 3.14 Model                                   */
/* Comments:                                                                */
/* This is a mix between Timohty Boger's Master's Thesis Implementation for */
/* the ZC702 and Daniel Ramirez's RTEMS implementation                      */
/****************************************************************************/
/*-----------------------------------------------------------
  Author: Timothy J Boger
  Date: 4/29/13 Task Switching
  Benchmark OS:FreeRTOS
  Platform: ZC702 Evaluation Board
  References:
   - “FreeRTOS Port for Xilinx Zynq Devices” FreeRTOS Ltd. February 12, 2013.
   -  R. Kar.. "Implementing the Rhealstone Real-Time Benchmark". 1990.
   -  Cory Nakaji. "MIO, EMIO and AXI GPIO LEDS for ZC702". 2013.
  Ported to RISC-V and FreeRTOS 10 by DornerWorks' Jesse Millwood (2019)
/*-----------------------------------------------------------*/

#include "FreeRTOS.h"
#include "rhealstone_utils.h"
#include "task.h"
#include "queue.h"
#include "timers.h"
#include "stdio.h"

//Benchmark Variables
// #define BENCHMARK_LOOPS 500000
#define BENCHMARK_LOOPS 100
//Accounting for extra Task3 switching
uint32_t count1 = 0;
uint32_t count2 = 0;
//*********************************************************
// Priorities at which the tasks are created
#define mainFIRST_TASK_PRIORITY  ( tskIDLE_PRIORITY + 2 )
#define mainSECOND_TASK_PRIORITY ( tskIDLE_PRIORITY + 2 )
#define mainTHIRD_TASK_PRIORITY ( tskIDLE_PRIORITY + 1 )

//*********************************************************
//Associate Functions with Tasks
static void prvFirst( void *pvParameters );
static void prvSecond( void *pvParameters );
static void prvReport( void *pvParameters );
//*********************************************************
//Task Handle
xTaskHandle xHandleFirst;
xTaskHandle xHandleSecond;
xTaskHandle xHandleReport;
extern xTaskHandle xIspTask;
//*********************************************************
/* Test Record Keeping */
mTaskSwitchTickRecord_t test_record;

int test_main( void )
{

    vTaskPrioritySet(&xIspTask, tskIDLE_PRIORITY + 3);
    test_positive();
    test_begin();
    /*****************************************************************
     Serial Non_Switching Measurement Measure execution time of task1 and
    task2 when they are executed serially (without task switching).
    Measure the time between the High and Low GPIO output
    /******************************************************************/
    test_record.baseline_begin_ticks = get_timer_value();
    for (count1 = 0; count1 < BENCHMARK_LOOPS; count1++)
    {
        //Do Nothing
    }
    for (count2 = 0; count2 < BENCHMARK_LOOPS; count2++)
    {
        // Do Nothing
    }
    test_record.baseline_end_ticks = get_timer_value();
    t_printf("Done taking baseline measurement\n");
    /*****************************************************************
    Task Switching Measurement Create three tasks. Task 1 and Task 2 will
    perform the task switching.

    Task 3 controls the start and finish of the program and sets the
    GPIO pin Measure the time between the High and Low GPIO output
    ******************************************************************/

    xTaskCreate( prvFirst, "Task 1", configMINIMAL_STACK_SIZE, NULL, mainFIRST_TASK_PRIORITY, &xHandleFirst  );
    xTaskCreate( prvSecond, "Task 2", configMINIMAL_STACK_SIZE, NULL, mainSECOND_TASK_PRIORITY, &xHandleSecond  );
    xTaskCreate( prvReport, "Report Task", configMINIMAL_STACK_SIZE, NULL, mainTHIRD_TASK_PRIORITY, &xHandleReport );

    vTaskSuspend( xHandleReport);
    taskYIELD();
}

//*********************************************************************
//Task 3
static void prvReport( void *pvParameters )
{
    uint32_t work_baseline_ticks;
    uint32_t work_switching_ticks;
    uint32_t switching_ticks;
    uint32_t timer_freq;
    uint32_t switching_time_usecs;

    vTaskDelete(xHandleFirst);
    vTaskDelete(xHandleSecond);

    work_baseline_ticks = (test_record.baseline_end_ticks - test_record.baseline_begin_ticks);
    work_switching_ticks = (test_record.measured_work_end_ticks - test_record.measured_work_begin_ticks);
    if (work_baseline_ticks > work_switching_ticks)
    {
        t_printf("ERROR: Ticks taken for baseline serial work is more than when using tasks\n");
        t_printf("       The baseline should be less\n");
        t_printf(" Baseline  : %lu\n", work_baseline_ticks);
        t_printf(" Switching : %lu\n", work_switching_ticks);
    }
    else
    {
        timer_freq = get_timer_freq();
        // Average Ticks per task switch
        switching_ticks = (work_switching_ticks - work_baseline_ticks)/((BENCHMARK_LOOPS *2) - 1);
        switching_time_usecs = ticks_to_usecs(switching_ticks);
        print_results_json("task_switching", "base", switching_ticks, timer_freq, switching_time_usecs);

    }
    vTaskResume(xIspTask);
    test_pass();
    test_done();
}
//*********************************************************************
//Task 1
static void prvFirst( void *pvParameters )
{
    // Runs First
    vTaskSuspend( xIspTask );
    test_record.measured_work_begin_ticks = get_timer_value();
    for (count1 = 0; count1 < BENCHMARK_LOOPS ; count1++)
    {
        taskYIELD();
    }
    test_record.measured_work_end_ticks = get_timer_value();
    vTaskPrioritySet(xHandleReport, tskIDLE_PRIORITY + 4);
    vTaskResume(xHandleReport);
    taskYIELD();
}
//*********************************************************************
//Task 2
static void prvSecond( void *pvParameters )
{
    for (count2 = 0; count2 < BENCHMARK_LOOPS -1; count2++)
    {
        taskYIELD();
    }
    taskYIELD();
}
/*-----------------------------------------------------------*/
