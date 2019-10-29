TEST_ROOT_DIR=..

CFLAGS := $(ISP_CFLAGS)

LDFLAGS += $(ISP_LDFLAGS)

INCLUDES += $(ISP_INCLUDES)
INCLUDES += -I$(TEST_ROOT_DIR)
INCLUDES += -I$(TEST_ROOT_DIR)/lzfx

SOURCES := lzfx.c lzfx_decomp.c
SOURCES += $(TEST_ROOT_DIR)/test_status.c
SOURCES += $(TEST_ROOT_DIR)/test.c

OBJECTS := $(patsubst %.c,%.o,$(SOURCES))

TARGET := $(OUTPUT_DIR)/lzfx

all: $(TARGET)

$(TARGET): $(ISP_OBJECTS) $(ISP_LIBS) $(ISP_DEPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) $(ISP_LIBS) $(ISP_OBJECTS) \
		$(OBJECTS) -o $@ $(LDFLAGS)

$(OBJECTS): %.o: %.c $(SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@
