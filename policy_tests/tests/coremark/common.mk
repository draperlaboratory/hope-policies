CFLAGS := $(ISP_CFLAGS)

CFLAGS += -DITERATIONS=2000 -DPERFORMANCE_RUN=1
CFLAGS += -O2 -fno-common -funroll-loops -finline-functions --param max-inline-insns-auto=20 -falign-functions=4 -falign-jumps=4 -falign-loops=4
CFLAGS += -DFLAGS_STR=\""$(CFLAGS)"\"

INCLUDES += $(ISP_INCLUDES)
INCLUDES += -I..

LDFLAGS += $(ISP_LDFLAGS)

SOURCES := $(wildcard *c)
SOURCES += ../test_status.c
SOURCES += ../test.c

OBJECTS := $(patsubst %.c,%.o,$(SOURCES))

TARGET := $(OUTPUT_DIR)/coremark

all: $(TARGET)

$(TARGET): $(ISP_OBJECTS) $(ISP_LIBS) $(ISP_DEPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) $(ISP_OBJECTS) \
		$(OBJECTS) -o $@ $(LDFLAGS)

$(OBJECTS): %.o: %.c $(SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@
