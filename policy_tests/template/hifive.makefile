TARGET = main
C_SRCS += ../test.c ../hifive.c ../test_status.c
CFLAGS += -O2 -fno-builtin-printf
RISCV_PATH ?= $(ISP_PREFIX)
RISCV_GCC     ?= $(abspath $(RISCV_PATH)/bin/riscv32-unknown-elf-gcc)
RISCV_GXX     ?= $(abspath $(RISCV_PATH)/bin/riscv32-unknown-elf-g++)
RISCV_OBJDUMP ?= $(abspath $(RISCV_PATH)/bin/riscv32-unknown-elf-objdump)
RISCV_GDB     ?= $(abspath $(RISCV_PATH)/bin/riscv32-unknown-elf-gdb)
RISCV_AR      ?= $(abspath $(RISCV_PATH)/bin/riscv32-unknown-elf-ar)

CC=$(RISCV_GCC)

RISCV_ARCH ?= rv32ima
RISCV_ABI ?= ilp32

BOARD ?= freedom-e300-hifive1
LINK_TARGET ?= flash

BSP_BASE = ./bsp
include $(BSP_BASE)/env/common.mk