RUNTIME ?= bare
include ../isp-runtime-$(RUNTIME).mk

TEST_CFLAGS := -DLOOP_FRAC=3
TEST_LDFLAGS := -lm
TEST_HELPER_DIR = ..
TEST_INCLUDES += -I$(TEST_HELPER_DIR)
TEST_SOURCES := $(wildcard *.c)
TEST_OBJECTS := $(patsubst %.c, %.o, $(TEST_SOURCES))

TEST_TARGET := $(OUTPUT_DIR)/basicmath

include ../common.mk
