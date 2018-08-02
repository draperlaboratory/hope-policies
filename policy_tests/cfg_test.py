# test script for running unit test

# Pull in possible configurations
from cfg_classes import configs

# Choose a test config from the classes defined in module testClasses
cfg = 'working'

# Which simulator to use for testing
simulator = "renode"
#simulator = "verilator"
#simulator = "fpga"
#simulator = "qemu"


# Nothing to configure below here

# helpers to fetch params from config
def os_modules():
    return configs[cfg].os_modules

def policies():
    return configs[cfg].policies
    
def positive_tests():
    return configs[cfg].positive_tests
    
def negative_tests():
    return configs[cfg].negative_tests
    
# Test that should work, but don't for a known reason
broken_tests = [ 
#"CFI/jump_data_fails_1.c"  # Awaiting a compiler fix for cfi metadata
]

# tests to be used with performance profiling target
profile_tests = [
#    "hello_works_1.c", 
    "stanford_int_treesort_fixed.c",
#    "malloc_prof_1.c",
#    "malloc_prof_2.c"
]

# quick uses -O2, All uses all 3
quick_opt = ["O2"]
more_opts = ["O1", "O3"]

# Delete test dirs for passing tests, note: easier to use make debug-xxx target instead
#    of editing this var
removePassing = False
