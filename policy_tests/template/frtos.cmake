cmake_minimum_required(VERSION 3.5) # or other version

if (NOT DEFINED ISP_PREFIX)
  set(ISP_PREFIX "/opt/isp/")
endif()

if (NOT DEFINED FREE_RTOS_DIR)
  set(FREE_RTOS_DIR "${ISP_PREFIX}/FreeRTOS")
endif()

if (NOT DEFINED CMAKE_TOOLCHAIN_FILE)
   set(CMAKE_TOOLCHAIN_FILE "${FREE_RTOS_DIR}/Demo/RISCV_MIV_GCC/riscv.cmake")
 endif()

if (NOT DEFINED CMAKE_BUILD_TYPE)
   set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)
endif()

project (FreeRTOS C ASM)

set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -T ${FREE_RTOS_DIR}/Demo/RISCV_MIV_GCC/MIV/link_miv.ld -nostartfiles")

set(WARNINGS "-Wall -Wextra -Wshadow -Wpointer-arith -Wbad-function-cast -Wcast-align -Wsign-compare")
set(WARNINGS "${WARNINGS} -Waggregate-return -Wstrict-prototypes -Wmissing-prototypes -Wmissing-declarations -Wunused")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D__gracefulExit ${WARNINGS} -Os -DNDEBUG -g")
#set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D__gracefulExit ${WARNINGS}")

include_directories("${FREE_RTOS_DIR}/Source/include")
include_directories("${FREE_RTOS_DIR}/Source/portable/GCC/RISCV")
include_directories("${FREE_RTOS_DIR}/Demo/RISCV_MIV_GCC/arch")
include_directories("${FREE_RTOS_DIR}/Demo/RISCV_MIV_GCC/conf")
include_directories("${FREE_RTOS_DIR}/Demo/RISCV_MIV_GCC/MIV/include")

add_library(free-rtos ${FREE_RTOS_DIR}/Source/tasks.c
		      ${FREE_RTOS_DIR}/Source/croutine.c
		      ${FREE_RTOS_DIR}/Source/queue.c
		      ${FREE_RTOS_DIR}/Source/timers.c
		      ${FREE_RTOS_DIR}/Source/event_groups.c
		      ${FREE_RTOS_DIR}/Source/list.c
		      ${FREE_RTOS_DIR}/Source/portable/MemMang/heap_2.c
		      ${FREE_RTOS_DIR}/Source/portable/Common/mpu_wrappers.c
		      ${FREE_RTOS_DIR}/Source/portable/GCC/RISCV/port.c
		      ${FREE_RTOS_DIR}/Source/portable/GCC/RISCV/portasm.S
		      ${FREE_RTOS_DIR}/Demo/RISCV_MIV_GCC/arch/syscall.c
		      ${FREE_RTOS_DIR}/Demo/RISCV_MIV_GCC/arch/utils.c
		      ${FREE_RTOS_DIR}/Demo/RISCV_MIV_GCC/arch/boot.S)

add_library(free-rtos-miv ${FREE_RTOS_DIR}/Demo/RISCV_MIV_GCC/MIV/src/miv_core_uart.c)

add_executable(main frtos.c test_status.c test.c)


target_link_libraries(main free-rtos free-rtos-miv)
