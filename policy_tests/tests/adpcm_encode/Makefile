RUNTIME ?= bare

include ../isp-runtime-$(RUNTIME).mk

ifndef LARGE_INPUT
   TEST_CFLAGS += -DINPUT_FRAC=20
endif

TEST_HELPER_DIR = ..
TEST_INCLUDES += -I$(TEST_HELPER_DIR)
TEST_SOURCES := adpcm.c rawcaudio.c
TEST_OBJECTS := $(patsubst %.c, %.o, $(TEST_SOURCES))

TEST_TARGET := $(OUTPUT_DIR)/adpcm_encode

include ../common.mk