CFLAGS += $(ISP_CFLAGS)

INCLUDES += $(ISP_INCLUDES)
INCLUDES += -I../..

LDFLAGS += $(ISP_LDFLAGS)

SOURCES := $(wildcard *c)
SOURCES += ../../test_status.c

OBJECTS := $(patsubst %.c,%.o,$(SOURCES))

TARGET := $(OUTPUT_DIR)/password/webapp_password_leak

all: $(TARGET)

$(TARGET): $(ISP_OBJECTS) $(ISP_LIBS) $(ISP_DEPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) $(ISP_LIBS) $(ISP_OBJECTS) \
		$(OBJECTS) -o $@ $(LDFLAGS)

$(OBJECTS): %.o: %.c $(SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@
