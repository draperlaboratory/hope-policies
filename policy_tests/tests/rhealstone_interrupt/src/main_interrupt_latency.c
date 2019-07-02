/****************************************************************************/
/* Author: Jesse Millwood                                                   */
/* Date: 4/25/19                                                            */
/* Deadlock Break Benchmark                                                 */
/* OS: FreeRTOS                                                             */
/* Plaform: RISC-V SiFIVE QEMU 3.14 Model                                   */
/****************************************************************************/

#include "FreeRTOS.h"
#include "rhealstone_utils.h"
#include "task.h"
#include "queue.h"
#include "timers.h"
#include "stdio.h"
#include "unistd.h"
#include "encoding.h"

#define BENCHMARK_LOOPS 1

//*********************************************************
// Priorities at which the tasks are created
#define mainFIRST_TASK_PRIORITY ( tskIDLE_PRIORITY + 4 )
#define mainSECOND_TASK_PRIORITY ( tskIDLE_PRIORITY + 3 )
#define mainTHIRD_TASK_PRIORITY ( tskIDLE_PRIORITY + 3 )
#define mainREPORT_TASK_PRIORITY ( tskIDLE_PRIORITY + 3 )
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
//*********************************************************

mTaskSwitchTickRecord_t test_record;
#define CLINT_MSIP_OFFSET     0

void handle_trap_rhealstone(void)
{
    test_record.measured_work_end_ticks = get_timer_value();
    CLINT_REG(CLINT_MSIP_OFFSET) = 0;
}

static inline void trigger_interrupt(void){
    set_csr(mie, MIP_MSIP); // Ensure Interrupt is enabled
    test_record.measured_work_begin_ticks = get_timer_value();
    // Write to memory mapped register to trigger machine software interrupt
    CLINT_REG(CLINT_MSIP_OFFSET) = 0x1;
}

//Main
int test_main( void )
{
    vTaskPrioritySet(&xIspTask, tskIDLE_PRIORITY + 3);
    test_positive();
    test_begin();

    vTaskSuspendAll();
    xTaskCreate( prvFirst, "Task 1", configMINIMAL_STACK_SIZE, NULL, mainFIRST_TASK_PRIORITY, &xHandleFirst );
    xTaskCreate( prvSecond, "Task 2", configMINIMAL_STACK_SIZE, NULL, mainSECOND_TASK_PRIORITY, &xHandleSecond );
    xTaskCreate( prvThird, "Task 3", configMINIMAL_STACK_SIZE, NULL, mainTHIRD_TASK_PRIORITY, &xHandleThird );
    xTaskCreate( prvReport, "Report", configMINIMAL_STACK_SIZE, NULL, mainREPORT_TASK_PRIORITY, &xHandleReport );
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
    vTaskDelete(xHandleSecond); //Delete Task 2
    vTaskDelete(xHandleThird); //Delete Task 3

    timer_freq = get_timer_freq();
    measured_ticks = (test_record.measured_work_end_ticks - test_record.measured_work_begin_ticks);
    measured_time_usecs = ticks_to_usecs(measured_ticks);

    print_results_json("interrupt_latency", "base", measured_ticks, timer_freq, measured_time_usecs);

    vTaskResume(xIspTask);
    test_pass();
    test_done();

}
//*********************************************************************
//Task 1
// Lower Priority task.
static void prvFirst( void *pvParameters )
{
    vTaskDelay(100);
    trigger_interrupt();
    vTaskPrioritySet(xHandleReport, tskIDLE_PRIORITY + 5);
    vTaskResume(xHandleReport);
    vTaskDelete(xHandleFirst);
}
//*********************************************************************
//Task 2
// Medium priority task. Only uses CPU time and sleep periodically.
static void prvSecond( void *pvParameters )
{
    for ( ;; )
    {

    }
}
//*********************************************************************
//Task 3
// High priority task. Potential deadlock when it tries to gain control
// of the "region" resource, because low-priority task holds region mostly.
static void prvThird( void *pvParameters )
{
    for( ;; )
    {

    }
}
