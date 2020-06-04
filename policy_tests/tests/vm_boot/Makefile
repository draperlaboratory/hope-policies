RUNTIME ?= bare
include ../isp-runtime-$(RUNTIME).mk

TEST_HELPER_DIR = ..
TEST_INCLUDES += -I$(TEST_HELPER_DIR)
TEST_SOURCES := $(wildcard *.c)
TEST_OBJECTS := $(TEST_SOURCES:%.c=%.o)

TEST_TARGET := $(OUTPUT_DIR)/vm_boot

include ../common.mk