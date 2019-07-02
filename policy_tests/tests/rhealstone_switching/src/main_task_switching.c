/*-----------------------------------------------------------
  Author: Timothy J Boger
  Date: 4/29/13
  Task Switching Benchmark
  OS:FreeRTOS
  Platform: ZC702 Evaluation Board
  References: - “FreeRTOS Port for Xilinx Zynq Devices” FreeRTOS Ltd. February 12, 2013.
  - R. Kar.. "Implementing the Rhealstone Real-Time Benchmark". 1990.
  - Cory Nakaji. "MIO, EMIO and AXI GPIO LEDS for ZC702". 2013.
/*-----------------------------------------------------------*/
// Includes
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "timers.h"
#include "xil_printf.h"
#include "stdio.h"
#include "xparameters.h"
#include "xgpio.h"
#include "xgpiops.h"
//**************************
//AXI Variables
static XGpioPs emio_pmod2;
#define EMIO_54 54
#define EMIO_55 55
#define EMIO_56 56
#define EMIO_57 57
//**************************
//Benchmark Variables
#define MAX_LOOPS_SERIAL 500000 //Max loops for simulation
#define MAX_LOOPS_TASK_SWITCHING 499999 //Accounting for extra Task3 switching
unsigned long count1 = 0, count2 = 0;
//*********************************************************
// Priorities at which the tasks are created
#define mainFIRST_TASK_PRIORITY  ( tskIDLE_PRIORITY + 2 )
#define mainSECOND_TASK_PRIORITY ( tskIDLE_PRIORITY + 2 )
#define mainTHIRD_TASK_PRIORITY  ( tskIDLE_PRIORITY + 3 )
//*********************************************************
//Associate Functions with Tasks
static void prvFirst( void *pvParameters );
static void prvSecond( void *pvParameters );
static void prvThird( void *pvParameters );
//*********************************************************
//Task Handle
xTaskHandle xHandleFirst;
xTaskHandle xHandleSecond;
xTaskHandle xHandleThird;
//*********************************************************
//Main
int main( void )
{
    prvInitializeExceptions();
//*******************************************************
//AXI Setup
    XGpioPs_Config *ConfigPtrPS;
    ConfigPtrPS = XGpioPs_LookupConfig(0);
    XGpioPs_CfgInitialize(&emio_pmod2, ConfigPtrPS,
                          ConfigPtrPS->BaseAddr);
//*******************************************************
//Setup PMOD 2 pins
    XGpioPs_SetDirectionPin(&emio_pmod2, EMIO_54, 1);
    XGpioPs_SetOutputEnablePin(&emio_pmod2, EMIO_54, 1);
    XGpioPs_SetDirectionPin(&emio_pmod2, EMIO_55, 1);
    XGpioPs_SetOutputEnablePin(&emio_pmod2, EMIO_55, 1);
    XGpioPs_SetDirectionPin(&emio_pmod2, EMIO_56, 1);
    XGpioPs_SetOutputEnablePin(&emio_pmod2, EMIO_56, 1);
    XGpioPs_SetDirectionPin(&emio_pmod2, EMIO_57, 1);
    XGpioPs_SetOutputEnablePin(&emio_pmod2, EMIO_57, 1);
//*******************************************************
//Setup PMOD 2 outputs to zero
    XGpioPs_WritePin(&emio_pmod2, EMIO_54, 0x0);
    XGpioPs_WritePin(&emio_pmod2, EMIO_55, 0x0);
    XGpioPs_WritePin(&emio_pmod2, EMIO_56, 0x0);
    XGpioPs_WritePin(&emio_pmod2, EMIO_57, 0x0);
//*******************************************************
//Start Benchmark
    xil_printf("Start of Task Switching Benchmark\n\r");
    xil_printf("Each task runs %D times\r\n", MAX_LOOPS_SERIAL);
/*****************************************************************
Serial Non_Switching Measurement
Measure execution time of task1 and task2 when they are executed
serially (without task switching).
Measure the time between the High and Low GPIO output
/******************************************************************/
    xil_printf("Start Serial Non_Switching Measurement\r\n");
    XGpioPs_WritePin(&emio_pmod2, EMIO_54, 0x1); //Set GPIO HIGH
    for (count1 = 0; count1 < MAX_LOOPS_SERIAL; count1++)
    {
//Do Nothing
    }
    for (count2 = 0; count2 < MAX_LOOPS_SERIAL; count2++)
    {
// Do Nothing
    }
    XGpioPs_WritePin(&emio_pmod2, EMIO_54, 0x0); //Set GPIO LOW
    xil_printf("Serial Non_Switching Measurement Done\r\n");
/*****************************************************************
Task Switching Measurement
Create three tasks. Task 1 and Task 2 will perform the task switching.
Task 3 controls the start and finish of the program and sets the GPIO pin
Measure the time between the High and Low GPIO output
******************************************************************/
    xil_printf("Start Task Switching Measurement\r\n");
//Create three tasks
    xTaskCreate( prvFirst, ( signed char * ) "F",
                 configMINIMAL_STACK_SIZE, NULL,
                 mainFIRST_TASK_PRIORITY, &xHandleFirst );
    xTaskCreate( prvSecond, ( signed char * ) "S",
                 configMINIMAL_STACK_SIZE, NULL,
                 mainSECOND_TASK_PRIORITY, &xHandleSecond );
    xTaskCreate( prvThird, ( signed char * ) "T",
                 configMINIMAL_STACK_SIZE, NULL,
                 mainTHIRD_TASK_PRIORITY, &xHandleThird );
    vTaskStartScheduler();
/* If all is well, the scheduler will now be running, and the following line
   will never be reached. If the following line does execute, then there was
   insufficient FreeRTOS heap memory available for the idle and/or timer tasks
   to be created. See the memory management section on the FreeRTOS web site
   for more details. */
    for( ;; );
}
//*********************************************************************
//Task 3
static void prvThird( void *pvParameters )
{
    for( ;; )
    {
//Runs First due to having highest priority
        XGpioPs_WritePin(&emio_pmod2, EMIO_54, 0x1); //Set GPIO HIGH
        vTaskPrioritySet(xHandleThird, tskIDLE_PRIORITY + 1);
//reduce priority below Task 1 and 2
//-------------------------- Task will yield here. Returns when Task 1 and 2 delete themselves
//xil_printf("LOW\r\n");
        XGpioPs_WritePin(&emio_pmod2, EMIO_54, 0x0); //Set GPIO LOW
        xil_printf("Task Switching Measurement Done\r\n");
        vTaskDelete(xHandleThird); //Delete Task 3
    }
}
//*********************************************************************
//Task 1
static void prvFirst( void *pvParameters )
{
    for( ;; )
    {
        for (count1 = 0; count1 < MAX_LOOPS_TASK_SWITCHING;
             count1++)
        {
            taskYIELD();
        }
        vTaskDelete(xHandleFirst); //Delete Task 1
    }
}
//*********************************************************************
//Task 2
static void prvSecond( void *pvParameters )
{
    for( ;; )
    {
        for (count2 = 0; count2 < MAX_LOOPS_TASK_SWITCHING;
             count2++)
        {
            taskYIELD();
        }
        vTaskDelete(xHandleSecond); //Delete Task 2
    }
}
//*********************************************************************
void vApplicationMallocFailedHook( void )
{
/* vApplicationMallocFailedHook() will only be called if
   configUSE_MALLOC_FAILED_HOOK is set to 1 in FreeRTOSConfig.h. It is a hook
   function that will get called if a call to pvPortMalloc() fails.
   pvPortMalloc() is called internally by the kernel whenever a task, queue or
   semaphore is created. It is also called by various parts of the demo
   application. If heap_1.c or heap_2.c are used, then the size of the heap
   available to pvPortMalloc() is defined by configTOTAL_HEAP_SIZE in
   FreeRTOSConfig.h, and the xPortGetFreeHeapSize() API function can be used
   to query the size of free heap space that remains (although it does not
   provide information on how the remaining heap might be fragmented). */
    taskDISABLE_INTERRUPTS();
    for( ;; );
}
//*********************************************************************
void vApplicationStackOverflowHook( xTaskHandle *pxTask, signed char *pcTaskName )
{
    ( void ) pcTaskName;
    ( void ) pxTask;
/* vApplicationStackOverflowHook() will only be called if
   configCHECK_FOR_STACK_OVERFLOW is set to either 1 or 2. The handle and name
   of the offending task will be passed into the hook function via its
   parameters. However, when a stack has overflowed, it is possible that the
   parameters will have been corrupted, in which case the pxCurrentTCB variable
   can be inspected directly. */
    taskDISABLE_INTERRUPTS();
    for( ;; );
}
//*********************************************************************
void vApplicationSetupHardware( void )
{
/* Do nothing */
}
