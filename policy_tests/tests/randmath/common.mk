TEST_ROOT_DIR=..

CFLAGS := $(ISP_CFLAGS)

LDFLAGS += $(ISP_LDFLAGS)

INCLUDES += $(ISP_INCLUDES)
INCLUDES += -I$(TEST_ROOT_DIR)
INCLUDES += -I$(TEST_ROOT_DIR)/randmath

SOURCES := abcmath.c main.c
SOURCES += $(TEST_ROOT_DIR)/test_status.c
SOURCES += $(TEST_ROOT_DIR)/test.c

OBJECTS := $(patsubst %.c,%.o,$(SOURCES))

TARGET := $(OUTPUT_DIR)/randmath

all: $(TARGET)

$(TARGET): $(ISP_OBJECTS) $(ISP_LIBS) $(ISP_DEPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) $(ISP_OBJECTS) \
		$(OBJECTS) -o $@ $(LDFLAGS)

abcmath.c: randmath
	./randmath

randmath: randmath.c
	gcc -o randmath randmath.c

$(OBJECTS): %.o: %.c $(SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@
