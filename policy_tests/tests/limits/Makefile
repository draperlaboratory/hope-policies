RUNTIME ?= bare
include ../isp-runtime-$(RUNTIME).mk

TEST_HELPER_DIR = ..
TEST_INCLUDES += -I$(TEST_HELPER_DIR)
TEST_SOURCES := limit_test.c limit_test.stuff.c
TEST_OBJECTS := $(patsubst %.c, %.o, $(TEST_SOURCES))

TEST_TARGET := $(OUTPUT_DIR)/limits

include ../common.mk