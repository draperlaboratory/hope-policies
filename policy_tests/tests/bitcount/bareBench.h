#ifdef BARE_METAL

//#include <stdio.h>
#include <stdint.h>

#include "encoding.h"
#include "uart_16550.h"

int benchmark();
int ee_printf(const char *fmt, ...);
void tohost_exit(uintptr_t code);  // From syscalls.c

#ifndef RUNS
#define RUNS 1
#endif

// Capture the current 64-bit cycle count.
uint64_t get_cycle_count() {
  #if __riscv_xlen == 64
    return read_csr(mcycle);
  #else
    // On 32-bit platforms, we need to concatenate the 32-bit `mcycle` and `mcycleh` CSRs. However, we need to be
    // careful and check that `mcycle` doesn't overflow and increment `mcycleh` after we have already read a stale
    // value of `mcycleh`. This short loop will avoid that issue.
    uint32_t cycle_lo, cycle_hi;
    asm volatile (
        "%=:\n\t"
        "csrr %1, mcycleh\n\t"
        "csrr %0, mcycle\n\t"
        "csrr t1, mcycleh\n\t"
        "bne  %1, t1, %=b"
      : "=r" (cycle_lo), "=r" (cycle_hi)
      : // No inputs.
      : "t1"
    );
    return (((uint64_t) cycle_hi) << 32) | (uint64_t) cycle_lo;
  #endif
}

int main(void)
{
  int run;
  uint64_t t_start, t_end;
  uint64_t test_duration_cycles;
  double test_duration_seconds;
  double iterations_per_second;

  // Initialize UART 16550 on the VCU118.
  uart0_init();
  ee_printf("Starting benchmark...\n");

  // Run baseline
  //puts("Baseline\n\r");
  //benchmark();
  t_start = get_cycle_count();
  for(run = 0; run < RUNS; ++run)
  {
    //puts("Trial\n\r");
    //printf("Run %d\n\r", run+1);
    if (benchmark() != 0) {
      ee_printf("FATAL ERROR: Benchmark failed.\n");
      tohost_exit(1);
    }
  }
  t_end = get_cycle_count();

  // Calculate and report benchmark duration.
  test_duration_cycles = t_end - t_start;
  test_duration_seconds = (double) test_duration_cycles / (double) CLOCKS_PER_SEC;
  iterations_per_second = (double) RUNS / test_duration_seconds;

  ee_printf("Iterations: %d\n", RUNS);
  ee_printf("Cycles elapsed: %llu\n", test_duration_cycles);
  ee_printf("Seconds elapsed: %f\n", test_duration_seconds);
  ee_printf("Iterations per second: %f\n", iterations_per_second);

  return 0;
}

#define printf(...)
#define fprintf(...)
#define fflush(...)
#define main(...) benchmark(__VA_ARGS__)

#endif
