RUNTIME ?= bare
include ../isp-runtime-$(RUNTIME).mk

TEST_CFLAGS := -O2 -fno-common -funroll-loops -finline-functions --param max-inline-insns-auto=20 -falign-functions=4 -falign-jumps=4 -falign-loops=4
TEST_CFLAGS += -DFLAGS_STR=\""$(TEST_CFLAGS)"\"

#XXX: hard-coding while debugging
#TEST_CFLAGS += -DITERATIONS=10000 -DPERFORMANCE_RUN=1
TEST_CFLAGS += -DITERATIONS=1 -DPERFORMANCE_RUN=1
TEST_HELPER_DIR = ..
TEST_INCLUDES += -I$(TEST_HELPER_DIR)
TEST_SOURCES := $(wildcard *c)
TEST_OBJECTS := $(patsubst %.c, %.o, $(TEST_SOURCES))

TEST_TARGET := $(OUTPUT_DIR)/coremark

include ../common.mk