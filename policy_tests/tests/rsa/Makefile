RUNTIME ?= bare
include ../isp-runtime-$(RUNTIME).mk

TEST_HELPER_DIR = ..
TEST_INCLUDES += -I$(TEST_HELPER_DIR)
TEST_SOURCES := main.c
TEST_OBJECTS := $(patsubst %.c, %.o, $(TEST_SOURCES))

TEST_TARGET := $(OUTPUT_DIR)/rsa

include ../common.mk