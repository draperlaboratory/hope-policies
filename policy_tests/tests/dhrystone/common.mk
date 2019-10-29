TEST_ROOT_DIR=..

CFLAGS += $(ISP_CFLAGS)
CFLAGS += -DDHRY_LOOPS=5000
INCLUDES += $(ISP_INCLUDES)
INCLUDES += -I$(TEST_ROOT_DIR)

LDFLAGS += $(ISP_LDFLAGS) --sysroot=${ISP_PREFIX}/riscv32-unknown-elf -L${ISP_PREFIX}/riscv32-unknown-elf/lib
LINKER_SCRIPT = dhrystone-baremetal.lds

SOURCES := dhrystone-baremetal.c
SOURCES += $(TEST_ROOT_DIR)/test_status.c
SOURCES += $(TEST_ROOT_DIR)/test.c

OBJECTS := $(patsubst %.c,%.o,$(SOURCES))

TARGET := $(OUTPUT_DIR)/dhrystone

all: $(TARGET)

$(TARGET): $(ISP_OBJECTS) $(ISP_LIBS) $(ISP_DEPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) $(ISP_LIBS) $(ISP_OBJECTS) \
		$(OBJECTS) -o $@ $(LDFLAGS)

$(OBJECTS): %.o: %.c $(SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@
