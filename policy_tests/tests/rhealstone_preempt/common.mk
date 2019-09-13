
TEST_ROOT_DIR = ..
CFLAGS += $(ISP_CFLAGS)
INCLUDES += $(ISP_INCLUDES)
INCLUDES += -I$(TEST_ROOT_DIR)
COMMON_RHEALSTONE_DIR=../rhealstone

# LD flags already defined as ISP_LDFLAGS
#LDFLAGS += $(ISP_LDFLAGS)

LINKER_SCRIPT = $(COMMON_RHEALSTONE_DIR)/lscript.ld
LDFLAGS += $(ISP_LDFLAGS) --sysroot=${ISP_PREFIX}/riscv32-unknown-elf -L${ISP_PREFIX}/riscv32-unknown-elf/lib

RHEAL_SRC_DIR = ./src
RHEAL_INC_DIR = ./include
RHEAL_FREERTOS_CONFIG_DIR = $(COMMON_RHEALSTONE_DIR)/rhealstone-freertos
FREERTOS_INC_DIR = $(ISP_PREFIX)/FreeRTOS/Source/include
FREERTOS_PORT_INC_DIR = $(ISP_PREFIX)/FreeRTOS/Source/portable/GCC/RISC-V
INCLUDES += -I$(RHEAL_INC_DIR) -I$(FREERTOS_INC_DIR) -I$(FREERTOS_PORT_INC_DIR)
INCLUDES += -I$(RHEAL_FREERTOS_CONFIG_DIR) -I$(COMMON_RHEALSTONE_DIR)/include

# ISP Test Suite Support _______________________________________________________
# Taking control of building freertos because I need to be able to change the config
ISP_LIBFREERTOS_PREEMPT = $(FREERTOS_BUILD_DIR)/libfreertos_preempt.a
ISP_LIBFREERTOS = $(ISP_LIBFREERTOS_PREEMPT)
ISP_LIB_INCS := $(foreach d, $(ISP_LIBFREERTOS), -L$(dir $d))
ISP_LIB_FLAGS := $(foreach d, $(ISP_LIBFREERTOS), -l$(patsubst lib%.a,%,$(notdir $d)))

# Common rhealstone test sources and objects ___________________________________
COMMON_RHEAL_SRCS = \
	$(COMMON_RHEALSTONE_DIR)/src/rhealstone_utils.c \
	$(TEST_ROOT_DIR)/test_status.c
COMMON_RHEAL_OBJS := $(patsubst %.c,%.o,$(COMMON_RHEAL_SRCS))

ifeq ($(OUTPUT_DIR),)
$(warning OUTPUT_DIR is undefined, setting to current directory)
OUTPUT_DIR = $(PWD)
endif

$(info CUR DIR         : $(PWD))
$(info RHEAL Source    : $(abspath $(RHEAL_SRC_DIR)))
$(info Output Dir      : $(abspath $(OUTPUT_DIR)))
$(info Includes        : $(INCLUDES))
$(info ISP LIBFREERTOS : $(ISP_LIBFREERTOS))
$(info LDFLAGS         : $(LDFLAGS))
$(info ISP OBJS        : $(ISP_OBJECTS))
$(info ISP LIB INCS    : $(ISP_LIB_INCS))
$(info ISP_LIB_FLAGS   : $(ISP_LIB_FLAGS))



# Set up targets _______________________________________________________________
RHEAL_PREEMPT_TARGET     = $(OUTPUT_DIR)/rhealstone_preempt
RHEAL_PREEMPT_SRC        = $(RHEAL_SRC_DIR)/main_preemption.c
RHEAL_PREEMPT_OBJ        =  $(patsubst %.c,%.o,$(RHEAL_PREEMPT_SRC))

.PHONY: clean-rhealstone clean-libfreertos clean-all build-libfreertos
all: $(RHEAL_PREEMPT_TARGET)

# Binary Targets _______________________________________________________________
$(RHEAL_PREEMPT_TARGET): $(ISP_OBJECTS) $(ISP_DEPS) $(ISP_LIBFREERTOS) $(COMMON_RHEAL_OBJS) $(RHEAL_PREEMPT_OBJ)
	$(CC) $(LDFLAGS) $(CFLAGS) $(INCLUDES) $(ISP_LIB_INCS) $(ISP_LIB_FLAGS) $(ISP_OBJECTS) \
	$(COMMON_RHEAL_OBJS) $(RHEAL_PREEMPT_OBJ) -o $@

# Object Targets  ______________________________________________________________
$(COMMON_RHEAL_OBJS): %.o: %.c $(COMMON_RHEAL_SRCS)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@

$(RHEAL_PREEMPT_OBJ): $(RHEAL_PREEMPT_SRC)
	$(CC) $(CFLAGS) $(INCLUDES) $< -c -o $@

# Libfreertos.a Variants _________________________________________________________
# The Rhealstone tests require different configurations of Freertos

$(ISP_LIBFREERTOS_PREEMPT):
	$(MAKE) -C $(FREERTOS_RVDEMO_DIR) FREERTOS_CONFIG_INC=$(abspath $(RHEAL_FREERTOS_CONFIG_DIR)) clean-libfreertos-objs
	$(MAKE) -C $(FREERTOS_RVDEMO_DIR) \
	FREERTOS_CONFIG_INC=$(abspath $(RHEAL_FREERTOS_CONFIG_DIR)) \
	build/libfreertos_preempt.a

build-libfreertos: $(ISP_LIBFREERTOS)

clean-rhealstone:
	find $(abspath $(dir $(RHEAL_SRC_DIR))) -name "*.o" -exec rm {} \;
clean-libfreertos:
	@$(MAKE) -C $(FREERTOS_RVDEMO_DIR) clean

clean-all: clean-rhealstone clean-libfreertos
