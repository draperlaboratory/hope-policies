/****************************************************************************/
/* Author: Jesse Millwood                                                   */
/* Date: 4/25/19                                                            */
/* Task Semaphore Shuffle Benchmark                                         */
/* OS: FreeRTOS                                                             */
/* Plaform: RISC-V SiFIVE QEMU 3.14 Model                                   */
/* Comments:                                                                */
/* This is a mix between Timohty Boger's Master's Thesis Implementation for */
/* the ZC702 and Daniel Ramirez's RTEMS implementation                      */
/****************************************************************************/
/*-----------------------------------------------------------
Author: Timothy J Boger
Date: 4/29/13
Semaphore Shuffle Benchmark
OS:FreeRTOS
Platform: ZC702 Evaluation Board
References: - “FreeRTOS Port for Xilinx Zynq Devices” FreeRTOS Ltd. February 12, 2013.
- R. Kar.. "Implementing the Rhealstone Real-Time Benchmark". 1990.
- Cory Nakaji. "MIO, EMIO and AXI GPIO LEDS for ZC702". 2013.
/*-----------------------------------------------------------*/

#include "FreeRTOS.h"
#include "rhealstone_utils.h"
#include "task.h"
#include "queue.h"
#include "timers.h"
#include "stdio.h"
#include "semphr.h"
//**************************
//Benchmark Variables
// #define BENCHMARK_LOOPS 100000
#define BENCHMARK_LOOPS 100
uint32_t count1 = 0, count2 = 0;

// 1= Yes 0 = No
#ifdef BENCH_USE_SEMAPHORE
uint32_t sem_exe = 1;
char test_variant[] = "with_semaphore";
#else
uint32_t sem_exe = 0;
char test_variant[] = "without_semaphore";
#endif

//*********************************************************
// Priorities at which the tasks are created
#define mainFIRST_TASK_PRIORITY ( tskIDLE_PRIORITY + 2 )
#define mainSECOND_TASK_PRIORITY ( tskIDLE_PRIORITY + 2 )
#define mainREPORT_TASK_PRIORITY ( tskIDLE_PRIORITY + 3 )
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
xSemaphoreHandle xSemaphore;
//*********************************************************

mTaskSwitchTickRecord_t test_record;
//Main
int test_main ( void )
{
    vTaskPrioritySet(&xIspTask, tskIDLE_PRIORITY + 3);
    test_positive();
    test_begin();
    /*****************************************************************
    Task Execution Time Without Semaphore Shuffling Measurement
    Create three tasks. Task 1 and Task 2 will perform the Task Execution.
    Task 3 controls the start and finish of the program and sets the GPIO pin
    Measure the time between the High and Low GPIO output
    Note: when sem_exe = 0;
    /*****************************************************************
    Semaphore Shuffling Measurement
    Create three tasks. Task 1 and Task 2 will perform Semaphore Shuffling.
    Time it takes a Task to acquire a semaphore that is owned by another equal priority task.
    Task 3 controls the start and finish of the program and sets the GPIO pin
    Measure the time between the High and Low GPIO output
    Note: when sem_exe = 1;
    /**********************************************************************/
    if (sem_exe == 1)
    {
        //Create Semaphore
        vSemaphoreCreateBinary(xSemaphore);
    }
    //Create three tasks
    xTaskCreate( prvFirst, "Task 1", configMINIMAL_STACK_SIZE, NULL, mainFIRST_TASK_PRIORITY, &xHandleFirst );
    xTaskCreate( prvSecond, "Task 2", configMINIMAL_STACK_SIZE, NULL, mainSECOND_TASK_PRIORITY, &xHandleSecond );
    xTaskCreate( prvReport, "Report", configMINIMAL_STACK_SIZE, NULL, mainREPORT_TASK_PRIORITY, &xHandleReport );
    vTaskSuspend(xHandleReport);
    taskYIELD();
}
//*********************************************************************
//Task 3
static void prvReport( void *pvParameters )
{
    uint32_t work_ticks;
    uint32_t measured_time;
    uint32_t timer_freq;

    vTaskDelete(xHandleFirst); //Delete Task 1
    vTaskDelete(xHandleSecond); //Delete Task 2

    timer_freq = get_timer_freq();
    work_ticks = (test_record.measured_work_end_ticks - test_record.measured_work_begin_ticks)/BENCHMARK_LOOPS;
    measured_time = ticks_to_usecs(work_ticks);

    print_results_json("semaphore_shuffle", &test_variant, work_ticks, timer_freq, measured_time);

    vTaskResume(xIspTask);
    test_pass();
    test_done();

}
//*********************************************************************
//Task 1
static void prvFirst( void *pvParameters )
{
     for( ;; )
    {
        for (count1 = 0; count1 < BENCHMARK_LOOPS; count1++)
        {
            if (sem_exe == 1)
            {
                xSemaphoreTake(xSemaphore, portMAX_DELAY);
            }
            taskYIELD();
            if (sem_exe == 1)
            {
                xSemaphoreGive(xSemaphore);
            }
            taskYIELD();
        }
        // printf("Done 1\n");
        vTaskSuspend(xHandleFirst);
    }
}
//*********************************************************************
//Task 2
static void prvSecond( void *pvParameters )
{
    // Starts First
    vTaskSuspend( xIspTask );
    test_record.measured_work_begin_ticks = get_timer_value();
    for( ;; )
    {
        for (count2 = 0; count2 < BENCHMARK_LOOPS; count2++)
        {
            if (sem_exe == 1)
            {
                xSemaphoreTake(xSemaphore, portMAX_DELAY);
            }
            taskYIELD();
            if (sem_exe == 1)
            {
                xSemaphoreGive(xSemaphore);
            }
            taskYIELD();
        }
        // Ends Last
        test_record.measured_work_end_ticks = get_timer_value();
        vTaskResume(xHandleReport);
        vTaskSuspend(xHandleSecond);

    }
}
