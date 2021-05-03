# All tests require these files.
TEST_HELPER_DIR     ?= .
TEST_HELPER_SOURCES := $(TEST_HELPER_DIR)/test.c
TEST_HELPER_SOURCES += $(TEST_HELPER_DIR)/test_status.c
TEST_HELPER_OBJECTS := $(patsubst %.c, %.o, $(TEST_HELPER_SOURCES))

# TEST_HELPER_ASM         := $(TEST_HELPER_DIR)/test_asm.S
TEST_HELPER_ASM :=
TEST_HELPER_ASM_OBJECTS := $(patsubst %.S,%.o,$(TEST_HELPER_ASM))

CFLAGS       += $(ISP_CFLAGS) $(TEST_CFLAGS)
ASM_FLAGS    += $(ISP_ASMFLAGS) $(TEST_ASMFLAGS)
INCLUDES     += -I. $(ISP_INCLUDES) $(TEST_INCLUDES)
LDFLAGS      += $(ISP_LDFLAGS) $(TEST_LDFLAGS)

TEST_SOURCES ?= $(patsubst %, %.c, $(shell basename $(TEST)))
TEST_OBJECTS ?= $(patsubst %.c, %.o, $(TEST_SOURCES))

C_OBJECTS    := $(TEST_HELPER_OBJECTS) $(TEST_OBJECTS)
ASM_OBJECTS  := $(TEST_ASM_OBJECTS) $(TEST_HELPER_ASM_OBJECTS)
OBJECTS      := $(C_OBJECTS) $(ASM_OBJECTS)

C_SOURCES    := $(TEST_HELPER_SOURCES) $(TEST_SOURCES) $(TEST_HELPER_ASM)
ASM_SOURCES  := $(TEST_HELPER_ASM)
SOURCES      := $(C_SOURCES) $(ASM_SOURCES)

TEST_TARGET ?= $(patsubst %, $(OUTPUT_DIR)/%, $(TEST))
TARGET := $(TEST_TARGET)

all: $(TARGET)

$(TARGET): $(ISP_OBJECTS) $(ISP_LIBS) $(ISP_DEPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) $(ISP_OBJECTS) $(OBJECTS) -o $@ $(LDFLAGS)

$(C_OBJECTS): %.o: %.c $(C_SOURCES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@

$(ASM_OBJECTS): %.o: %.S $(ASM_SOURCES)
	$(CC) $(ASM_FLAGS) $(INCLUDES) $< -c -o $@
