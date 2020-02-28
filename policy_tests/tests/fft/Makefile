RUNTIME ?= bare
include ../isp-runtime-$(RUNTIME).mk

TEST_LDFLAGS := -lm
TEST_CFLAGS := -DARRAYSIZE=256
TEST_HELPER_DIR = ..
TEST_INCLUDES += -I$(TEST_HELPER_DIR)
TEST_SOURCES := main.c fftmisc.c fourierf.c
TEST_OBJECTS := $(patsubst %.c, %.o, $(TEST_SOURCES))

TEST_TARGET := $(OUTPUT_DIR)/fft

include ../common.mk