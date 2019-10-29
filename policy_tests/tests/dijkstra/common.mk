TEST_ROOT_DIR=..

CFLAGS := $(ISP_CFLAGS)
CFLAGS += -DNUM_NODES=30

LDFLAGS += $(ISP_LDFLAGS)

INCLUDES += $(ISP_INCLUDES)
INCLUDES += -I$(TEST_ROOT_DIR)
INCLUDES += -I$(TEST_ROOT_DIR)/dijkstra

SOURCES := dijkstra.c
SOURCES += $(TEST_ROOT_DIR)/test_status.c
SOURCES += $(TEST_ROOT_DIR)/test.c

OBJECTS := $(patsubst %.c,%.o,$(SOURCES))

TARGET := $(OUTPUT_DIR)/dijkstra

all: $(TARGET)

$(TARGET): $(ISP_OBJECTS) $(ISP_LIBS) $(ISP_DEPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) $(ISP_LIBS) $(ISP_OBJECTS) \
		$(OBJECTS) -o $@ $(LDFLAGS)

$(OBJECTS): %.o: %.c $(SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@
