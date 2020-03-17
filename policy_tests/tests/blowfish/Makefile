RUNTIME ?= bare
include ../isp-runtime-$(RUNTIME).mk

TEST_CFLAGS := -DSMALL_INPUT
TEST_HELPER_DIR = ..
TEST_INCLUDES += -I$(TEST_HELPER_DIR)
TEST_SOURCES := blowfish_test.c blowfish.c
TEST_OBJECTS := $(patsubst %.c, %.o, $(TEST_SOURCES))

TEST_TARGET := $(OUTPUT_DIR)/blowfish

include ../common.mk