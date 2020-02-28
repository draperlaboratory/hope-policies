RUNTIME ?= bare
include ../isp-runtime-$(RUNTIME).mk

TEST_CFLAGS := -DLOOPS=10
TEST_HELPER_DIR = ..
TEST_INCLUDES += -I$(TEST_HELPER_DIR)
TEST_SOURCES := bmhasrch.c bmhisrch.c bmhsrch.c main.c
TEST_OBJECTS := $(patsubst %.c, %.o, $(TEST_SOURCES))

TEST_TARGET := $(OUTPUT_DIR)/stringsearch

include ../common.mk