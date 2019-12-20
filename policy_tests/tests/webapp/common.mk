CFLAGS += $(ISP_CFLAGS)

INCLUDES += $(ISP_INCLUDES)
INCLUDES += -I$(TEST_ROOT_DIR)
INCLUDES += -I$(TEST_ROOT_DIR)/webapp

LDFLAGS += $(ISP_LDFLAGS)

SOURCES := $(wildcard *c)
SOURCES := $(wildcard $(TEST_ROOT_DIR)/webapp/*.c)
SOURCES += $(TEST_ROOT_DIR)/test_status.c
SOURCES += $(TEST_ROOT_DIR)/test.c
SOURCES += $(TEST_SOURCE)

OBJECTS := $(patsubst %.c,%.o,$(SOURCES))

TARGET := $(OUTPUT_DIR)/$(TEST)

all: $(TARGET)

$(TARGET): $(ISP_OBJECTS) $(ISP_LIBS) $(ISP_DEPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) $(ISP_OBJECTS) \
		$(OBJECTS) -o $@ $(LDFLAGS)

$(OBJECTS): %.o: %.c $(SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@
