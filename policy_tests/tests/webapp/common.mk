TEST_HELPER_DIR = $(realpath ..)
TEST_INCLUDES := -I$(TEST_HELPER_DIR) -I$(TEST_HELPER_DIR)/webapp
TEST_SOURCES += $(wildcard $(TEST_HELPER_DIR)/webapp/*.c)

include ../common.mk
