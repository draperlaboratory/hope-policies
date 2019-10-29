CFLAGS += $(ISP_CFLAGS)
CFLAGS += -O0
CFLAGS += -DATTACK_TECHNIQUE=\"$(TECHNIQUE)\" \
					-DATTACK_INJECT_PARAM=\"$(INJECT_PARAM)\" \
					-DATTACK_CODE_PTR=\"$(CODE_PTR)\" \
					-DATTACK_LOCATION=\"$(LOCATION)\" \
					-DATTACK_FUNCTION=\"$(FUNCTION)\"

INCLUDES += $(ISP_INCLUDES)
INCLUDES += -I..

LDFLAGS += $(ISP_LDFLAGS)

SOURCES := $(wildcard *c)
SOURCES += ../test_status.c
SOURCES += ../test.c

OBJECTS := $(patsubst %.c,%.o,$(SOURCES))

TARGET := $(OUTPUT_DIR)/ripe/ripe-$(TECHNIQUE)-$(INJECT_PARAM)-$(CODE_PTR)-$(LOCATION)-$(FUNCTION)

all: $(TARGET)

$(TARGET): $(ISP_OBJECTS) $(ISP_LIBS) $(ISP_DEPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) $(ISP_LIBS) $(ISP_OBJECTS) \
		$(OBJECTS) -o $@ $(LDFLAGS)

$(OBJECTS): %.o: %.c $(SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@
