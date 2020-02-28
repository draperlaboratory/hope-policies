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

ASM_SOURCES := $(TEST_ROOT_DIR)/test_asm.S

C_OBJECTS := $(patsubst %.c,%.o,$(SOURCES))
ASM_OBJECTS := $(patsubst %.S,%.o,$(ASM_SOURCES))
OBJECTS := $(C_OBJECTS) $(ASM_OBJECTS)

TARGET := $(OUTPUT_DIR)/dhrystone

all: $(TARGET)

$(TARGET): $(ISP_OBJECTS) $(ISP_LIBS) $(ISP_DEPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) $(ISP_OBJECTS) \
		$(OBJECTS) -o $@ $(LDFLAGS)

$(C_OBJECTS): %.o: %.c $(SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@

$(ASM_OBJECTS): %.o: %.S $(SOURCES)
	$(CC) $(ASM_FLAGS) $(INCLUDES) $< -c -o $@
