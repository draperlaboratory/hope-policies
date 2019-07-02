/****************************************************************************/
/* Author: Jesse Millwood                                                   */
/* Date: 4/25/19                                                            */
/* Deadlock Break Benchmark                                                 */
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
#include "semphr.h"

//Benchmark Variables
// #define BENCHMARK_LOOPS 10000 //Max loops for simulation 10000
// This has been reduced so that it can run within the time alloted by the test framework
#define BENCHMARK_LOOPS 5
#define ONE_TICK 256100 //Number dependent on CPU. Must be longer than sleep period.

uint32_t count1 = 0;
uint32_t count2 = 0;
uint32_t count3 = 0;
uint32_t i;
uint32_t j;

uint32_t task1_init = 0;

#ifdef BENCH_USE_DEADLOCKING
uint32_t dead_brk = 1; //Run tasks with/without deadlocking 0 = without, 1 = with
char test_variant[20] = "with_deadlock";
#else
uint32_t dead_brk = 0;
char test_variant[20] = "without_deadlock";
#endif


//*********************************************************
// Priorities at which the tasks are created
#define mainFIRST_TASK_PRIORITY ( tskIDLE_PRIORITY + 2 )
#define mainSECOND_TASK_PRIORITY ( tskIDLE_PRIORITY + 3 )
#define mainTHIRD_TASK_PRIORITY ( tskIDLE_PRIORITY + 4 )
#define mainREPORT_TASK_PRIORITY ( tskIDLE_PRIORITY + 5 )
//*********************************************************
//Associate Functions with Tasks
static void prvFirst( void *pvParameters );
static void prvSecond( void *pvParameters );
static void prvThird( void *pvParameters );
static void prvReport( void *pvParameters );
//*********************************************************
//Task Handle
xTaskHandle xHandleFirst;
xTaskHandle xHandleSecond;
xTaskHandle xHandleThird;
xTaskHandle xHandleReport;
extern xTaskHandle xIspTask;
xSemaphoreHandle xMutex;
//*********************************************************

mTaskSwitchTickRecord_t test_record;

//Main
int test_main ( void )
{
    vTaskPrioritySet(&xIspTask, tskIDLE_PRIORITY + 3);
    test_positive();
    test_begin();

    /*****************************************************************
    Execution Time Measurement Without Deadlocks
    Create four tasks.
    Task 1 Lowest Priority
    Task 2 Medium Priority. Only uses CPU time and sleeps periodically.
    Task 3 Highest Priority. Potential deadlock when it tries to gain control
    of the "region" resource, because low-priority task holds region mostly.
    Task 4 controls the start and finish of the program and sets the GPIO pin
    Note: when dead_brk = 0;
    /*****************************************************************
    Deadlock Resolution Measurement
    Create four tasks.
    Task 1 Lowest Priority
    Task 2 Medium Priority. Only uses CPU time and sleeps periodically.
    Task 3 Highest Priority. Potential deadlock when it tries to gain control
    of the "region" resource, because low-priority task holds region mostly.
    Task 4 controls the start and finish of the program and sets the GPIO pin
    Measure the time between the High and Low GPIO output
    Note: when dead_brk = 1;
    /**********************************************************************/

    //Create Semaphore
    xMutex = xSemaphoreCreateMutex();
    vTaskSuspendAll();
    xTaskCreate( prvFirst, "Task 1", configMINIMAL_STACK_SIZE, NULL, mainFIRST_TASK_PRIORITY, &xHandleFirst );
    xTaskCreate( prvSecond, "Task 2", configMINIMAL_STACK_SIZE, NULL, mainSECOND_TASK_PRIORITY, &xHandleSecond );
    xTaskCreate( prvThird, "Task Deadlock", configMINIMAL_STACK_SIZE, NULL, mainTHIRD_TASK_PRIORITY, &xHandleThird );
    xTaskCreate( prvReport, "Report", configMINIMAL_STACK_SIZE, NULL, mainREPORT_TASK_PRIORITY, &xHandleReport );
    vTaskSuspend( xHandleSecond);
    vTaskSuspend( xHandleThird);
    vTaskSuspend( xHandleReport);
    xTaskResumeAll();

}
//*********************************************************************
//Task 4
static void prvReport( void *pvParameters )
{
    uint32_t measured_ticks;
    uint32_t measured_time_usecs;
    uint32_t timer_freq;

    vTaskDelete(xHandleFirst); //Delete Task 1

    timer_freq = get_timer_freq();
    measured_ticks = (test_record.measured_work_end_ticks - test_record.measured_work_begin_ticks)/BENCHMARK_LOOPS;
    measured_time_usecs = ticks_to_usecs(measured_ticks);

    print_results_json("deadlock_break", &test_variant, measured_ticks, timer_freq, measured_time_usecs);

    vTaskResume(xIspTask);
    test_pass();
    test_done();
}
//*********************************************************************
//Task 1
// Lower Priority task.
static void prvFirst( void *pvParameters )
{
    /* Allow to initially take the semaphore and be preempted by task 2 */
    xSemaphoreTake(xMutex, portMAX_DELAY); //Take control
    // This flag is to mark that the semaphore has been taken during
    // the task initialization. This is so that the task 1 has the semaphore
    // before task 3 starts. In the loop, however, the semaphore take can not
    // be called again otherwise this task will block itself
    task1_init = 1;
    vTaskResume(xHandleSecond);

    for( ;; )
    {
        if (count1 == BENCHMARK_LOOPS)
        {
            // task is done
            vTaskResume(xHandleReport);
        }

        if (task1_init == 0)
        {
            xSemaphoreTake(xMutex, portMAX_DELAY); //Take control
        }
        task1_init = 0;
        for (i = 0; i < ONE_TICK; i++) //delay loop
        {
            //Do Nothing
        }
        xSemaphoreGive(xMutex); //Release control
        count1++;
    }
}
//*********************************************************************
//Task 2
// Medium priority task. Only uses CPU time and sleep periodically.

static void prvSecond( void *pvParameters )
{
    /* Allow to initialize self and suspend for highest task */
    vTaskResume(xHandleThird);
    for( ;; )
    {
        if (count2 == BENCHMARK_LOOPS)
        {
            // Task is done
            vTaskDelete(xHandleSecond);
        }
        for (j = 0; j < ONE_TICK/4; j++) //delay loop
        {
            //Do Nothing
        }
        vTaskDelay(1); //Delay a single tick, allow preemption after for loop work?
        count2++;
    }
}
//*********************************************************************
//Task 3
// High priority task. Potential deadlock when it tries to gain control
// of the "region" resource, because low-priority task holds region mostly.
static void prvThird( void *pvParameters )
{

    /* All testing tasks are ready by now, and task 1 has semaphore */
    vTaskSuspend( xIspTask );
    test_record.measured_work_begin_ticks = get_timer_value();
    for( ;; )
    {
        if (count3 == BENCHMARK_LOOPS)
	{
            // Task is done
            test_record.measured_work_end_ticks = get_timer_value();
            vTaskDelete(xHandleThird);
        }
        vTaskDelay(3); //Delay a single tick
        i = ONE_TICK; //Reset Task 1
        if (dead_brk == 1)
        {
            xSemaphoreTake(xMutex, portMAX_DELAY); //Take control
            xSemaphoreGive(xMutex); //Release control
        }
        count3++;
    }
}
