# All tests require these files.
TEST_HELPER_DIR     ?= .
TEST_HELPER_SOURCES := $(TEST_HELPER_DIR)/test.c
TEST_HELPER_SOURCES += $(TEST_HELPER_DIR)/test_status.c
TEST_HELPER_OBJECTS := $(patsubst %.c, %.o, $(TEST_HELPER_SOURCES))

CFLAGS       += $(ISP_CFLAGS) $(TEST_CFLAGS)
INCLUDES     += -I. $(ISP_INCLUDES) $(TEST_INCLUDES)
LDFLAGS      += $(ISP_LDFLAGS) $(TEST_LDFLAGS)

TEST_SOURCES ?= $(patsubst %, %.c, $(shell basename $(TEST)))
TEST_OBJECTS ?= $(patsubst %.c, %.o, $(TEST_SOURCES))

OBJECTS      := $(TEST_HELPER_OBJECTS) $(TEST_OBJECTS)
SOURCES      := $(TEST_HELPER_SOURCES) $(TEST_SOURCES)

TEST_TARGET ?= $(patsubst %, $(OUTPUT_DIR)/%, $(TEST))
TARGET := $(TEST_TARGET)

all: $(TARGET)

$(TARGET): $(ISP_OBJECTS) $(ISP_LIBS) $(ISP_DEPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) $(ISP_OBJECTS) $(OBJECTS) -o $@ $(LDFLAGS)

$(OBJECTS): %.o: %.c $(SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@