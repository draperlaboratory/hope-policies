/****************************************************************************/
/* Author: Jesse Millwood                                                   */
/* Date: 4/25/19                                                            */
/* Task Intertask Latency Benchmark                                         */
/* OS: FreeRTOS                                                             */
/* Plaform: RISC-V SiFIVE QEMU 3.14 Model                                   */
/* Comments:                                                                */
/* This is a mix between Timohty Boger's Master's Thesis Implementation for */
/* the ZC702 and Daniel Ramirez's RTEMS implementation                      */
/****************************************************************************/
/*-----------------------------------------------------------
Author: Timothy J Boger
Date: 4/29/13
Inter-Task Message Latency Benchmark
OS:FreeRTOS
Platform: ZC702 Evaluation Board
References: - “FreeRTOS Port for Xilinx Zynq Devices” FreeRTOS Ltd. February 12, 2013.
- R. Kar.. "Implementing the Rhealstone Real-Time Benchmark". 1990.
- Cory Nakaji. "MIO, EMIO and AXI GPIO LEDS for ZC702". 2013.
/*-----------------------------------------------------------*/
// Includes
#include "FreeRTOS.h"
#include "rhealstone_utils.h"
#include "task.h"
#include "queue.h"
#include "timers.h"
#include "stdio.h"

//Benchmark Variables
//Max loops for simulation
// #define BENCHMARK_LOOPS 1000000
#define BENCHMARK_LOOPS 100
char msg_buf[10] = "MESSAGE", recv_buf[10];
#define Queue_Length 10
#define Queue_Item_Size sizeof(msg_buf)
unsigned long count1, count2;
//*********************************************************
// Priorities at which the tasks are created
#define mainFIRST_TASK_PRIORITY ( tskIDLE_PRIORITY + 2 )
#define mainSECOND_TASK_PRIORITY ( tskIDLE_PRIORITY + 3 )
#define mainREPORT_TASK_PRIORITY ( tskIDLE_PRIORITY + 4 )
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
xQueueHandle xQueue;
extern xTaskHandle xIspTask;
//*********************************************************

mTaskSwitchTickRecord_t test_record;
//Main
int test_main ( void )
{

    vTaskPrioritySet(&xIspTask, tskIDLE_PRIORITY + 3);
    test_positive();
    test_begin();

    // Create Message Queue
    xQueue = xQueueCreate(Queue_Length, Queue_Item_Size);
    if(xQueue == NULL)
    {
        //The queue could not be created
        t_printf("Queue Create Error\n\r");
    }
    /***********************************************************************
    Serial Execution Measurement Without Messages
    Measure execution time of task1 and task2 when they are executed
    serially (without messages).
    Measure the time between the High and Low GPIO output
    /**********************************************************************/

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
    /***********************************************************************
    Inter-Task Message Latency Measurement
    Create three tasks. Task 1 and Task 2 will perform the Messaging.
    Task 1 sends messages, Task 2 receives them.
    Task 2 has a higher priority than Task 1 to make sure it receives messages immediately
    Task 3 controls the start and finish of the program and sets the GPIO pin
    Measure the time between the High and Low GPIO output
    ***********************************************************************/
    t_printf("Start Inter-Task Message Latency Measurement\r\n");
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
    uint32_t work_baseline_ticks;
    uint32_t work_measured_ticks;
    uint32_t measured_ticks;
    uint32_t measured_time;
    uint32_t timer_freq;

    vTaskDelete(xHandleFirst);
    vTaskDelete(xHandleSecond);

    t_printf("Inter-Task Message Latency Measurement Done\r\n");
    timer_freq = get_timer_freq();
    work_measured_ticks = test_record.measured_work_end_ticks - test_record.measured_work_begin_ticks;
    work_baseline_ticks = test_record.baseline_end_ticks - test_record.baseline_begin_ticks;
    measured_ticks = (work_measured_ticks - work_baseline_ticks)/BENCHMARK_LOOPS;
    measured_time = ticks_to_usecs(measured_ticks);

    print_results_json("intertask latency", "base", measured_ticks, timer_freq, measured_time);

    vQueueDelete(xQueue); //Delete Queue

    vTaskResume(xIspTask);
    test_pass();
    test_done();

}
//*********************************************************************
//Task 1 - Sends Messages
static void prvFirst( void *pvParameters )
{
    for( ;; )
    {
        for (count1 = 0; count1 < BENCHMARK_LOOPS; count1++)
        {
            if(xQueueSendToBack(xQueue, msg_buf, portMAX_DELAY)!=pdPASS)
            {
                //Nothing could be sent blocking timer expired
                t_printf("Sent Blocking Timer Ran Out \r\n");
            }
        }
        vTaskSuspend(xHandleFirst);
    }

}
//*********************************************************************
//Task 2
static void prvSecond( void *pvParameters )
{
    // starts first
    vTaskSuspend( xIspTask );
    test_record.measured_work_begin_ticks = get_timer_value();
    for( ;; )
    {
        for (count2 = 0; count2 < BENCHMARK_LOOPS; count2++)
        {
            if(xQueueReceive(xQueue, recv_buf, portMAX_DELAY)!= pdPASS)
            {
                //Nothing Received because blocking timer expired
                t_printf("Receive Blocking Timer Ran Out \r\n");
            }
        }
        // ends last
        test_record.measured_work_end_ticks = get_timer_value();
        vTaskResume(xHandleReport);
        vTaskSuspend(xHandleSecond);
    }
}
