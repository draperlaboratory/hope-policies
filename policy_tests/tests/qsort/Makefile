RUNTIME ?= bare
include ../isp-runtime-$(RUNTIME).mk

TEST_LDFLAGS := -lm
TEST_HELPER_DIR = ..
TEST_INCLUDES += -I$(TEST_HELPER_DIR)
TEST_SOURCES := qsort_large.c
TEST_OBJECTS := $(patsubst %.c, %.o, $(TEST_SOURCES))

TEST_TARGET := $(OUTPUT_DIR)/qsort

include ../common.mk