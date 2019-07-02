#include "FreeRTOS.h"
#include "stdio.h"
#include "rhealstone_utils.h"
#include "test.h"

uint32_t ticks_to_usecs(uint32_t ticks)
{
    uint32_t scale = 1000;
    uint32_t scaled_ticks = ticks * scale;
    uint32_t scaled_freq = get_timer_freq() / scale;
    return scaled_ticks / scaled_freq;
}

void print_results_json(char* name, char* variant, uint32_t ticks, uint32_t timer_freq, uint32_t time_result_us)
{
    t_printf("RESULTS BEGIN:\n");
    t_printf("{\"rhealstone_result\": {\n");
    t_printf(" \"name\":\"%s\", \n", name);
    t_printf(" \"variant\": \"%s\", \n", variant);
    t_printf(" \"ticks\":\"%lu\", \n", ticks);
    t_printf(" \"cpu_frequency\":\"%lu\", \n", timer_freq);
    t_printf(" \"measure_usecs\":\"%lu\" \n", time_result_us);
    t_printf(" }\n");
    t_printf("}\n");
    t_printf("RESULTS END\n");
}
