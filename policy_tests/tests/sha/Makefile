RUNTIME ?= bare
include ../isp-runtime-$(RUNTIME).mk

TEST_CFLAGS := -DSMALL_INPUT -DLITTLE_ENDIAN -DUSE_MODIFIED_SHA
TEST_HELPER_DIR = ..
TEST_INCLUDES += -I$(TEST_HELPER_DIR)
TEST_SOURCES := main.c sha.c
TEST_OBJECTS := $(patsubst %.c, %.o, $(TEST_SOURCES))

TEST_TARGET := $(OUTPUT_DIR)/sha

include ../common.mk