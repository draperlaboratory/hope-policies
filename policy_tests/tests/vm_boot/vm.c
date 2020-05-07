#include <stdint.h>
#include <string.h>
#include "encoding.h"

#define MAX_TEST_PAGES 255

#define PGSHIFT 12
#define PGSIZE (1UL << PGSHIFT)

#define SIZEOF_TRAPFRAME_T ((__riscv_xlen / 8) * 36)

typedef unsigned long pte_t;
#define LEVELS (sizeof(pte_t) == sizeof(uint64_t) ? 3 : 2)
#define PTIDXBITS (PGSHIFT - (sizeof(pte_t) == 8 ? 3 : 2))
#define VPN_BITS (PTIDXBITS * LEVELS)
#define VA_BITS (VPN_BITS + PGSHIFT)
#define PTES_PER_PT (1UL << RISCV_PGLEVEL_BITS)
#define MEGAPAGE_SIZE (PTES_PER_PT * PGSIZE)

typedef struct
{
  long gpr[32];
  long sr;
  long epc;
  long badvaddr;
  long cause;
} trapframe_t;

void trap_entry();
void pop_tf(trapframe_t*);

volatile uint64_t tohost;
volatile uint64_t fromhost;

static void do_tohost(uint64_t tohost_value)
{
  while (tohost)
    fromhost = 0;
  tohost = tohost_value;
}

#define pa2kva(pa) ((void*)(pa) - DRAM_BASE - MEGAPAGE_SIZE)
#define uva2kva(pa) ((void*)(pa) - MEGAPAGE_SIZE)

#define flush_page(addr) asm volatile ("sfence.vma %0" : : "r" (addr) : "memory")

static void do_exit(int code)
{
  do_tohost((code << 1) | 1);
  while (1);
}

#define assert(x) do { \
  if (x) break; \
  do_exit(1); \
} while(0)

#define l1pt pt[0]
#define user_l2pt pt[1]
#if __riscv_xlen == 64
# define NPT 5
#define kernel_l2pt pt[2]
# define user_l3pt pt[3]
#define tohost_l3pt pt[4]
#else
# define NPT 3
# define user_l3pt user_l2pt
#define tohost_l3pt pt[2]
#endif
pte_t pt[NPT][PTES_PER_PT] __attribute__((aligned(PGSIZE)));

typedef struct { pte_t addr; void* next; } freelist_t;

freelist_t user_mapping[MAX_TEST_PAGES];
freelist_t freelist_nodes[MAX_TEST_PAGES];
freelist_t *freelist_head, *freelist_tail;

static void evict(unsigned long addr)
{
  assert(addr >= PGSIZE && addr < MAX_TEST_PAGES * PGSIZE);
  addr = addr/PGSIZE*PGSIZE;

  freelist_t* node = &user_mapping[addr/PGSIZE];
  if (node->addr)
  {
    // check accessed and dirty bits
    assert(user_l3pt[addr/PGSIZE] & PTE_A);
    uintptr_t sstatus = set_csr(sstatus, SSTATUS_SUM);
    if (memcmp((void*)addr, uva2kva(addr), PGSIZE)) {
      assert(user_l3pt[addr/PGSIZE] & PTE_D);
      memcpy((void*)addr, uva2kva(addr), PGSIZE);
    }
    write_csr(sstatus, sstatus);

    user_mapping[addr/PGSIZE].addr = 0;

    if (freelist_tail == 0)
      freelist_head = freelist_tail = node;
    else
    {
      freelist_tail->next = node;
      freelist_tail = node;
    }
  }
}

void __attribute__((noinline)) insncpy(void* dest, const void* src, size_t n)
{
  uint32_t* insn_dest = (uint32_t*)dest;
  uint32_t* insn_src = (uint32_t*)src;
  for (size_t i = 0; i < n/sizeof(uint32_t); i++)
    insn_dest[i] = insn_src[i];
}

void handle_fault(uintptr_t addr, uintptr_t cause)
{
  assert(addr >= PGSIZE && addr < MAX_TEST_PAGES * PGSIZE);
  addr = addr/PGSIZE*PGSIZE;

  if (user_l3pt[addr/PGSIZE]) {
    if (!(user_l3pt[addr/PGSIZE] & PTE_A)) {
      user_l3pt[addr/PGSIZE] |= PTE_A;
    } else {
      assert(!(user_l3pt[addr/PGSIZE] & PTE_D) && cause == CAUSE_STORE_PAGE_FAULT);
      user_l3pt[addr/PGSIZE] |= PTE_D;
    }
    flush_page(addr);
    return;
  }

  freelist_t* node = freelist_head;
  assert(node);
  freelist_head = node->next;
  if (freelist_head == freelist_tail)
    freelist_tail = 0;

  uintptr_t new_pte = (node->addr >> PGSHIFT << PTE_PPN_SHIFT) | PTE_V | PTE_U | PTE_R | PTE_W | PTE_X;
  user_l3pt[addr/PGSIZE] = new_pte | PTE_A | PTE_D;
  flush_page(addr);

  assert(user_mapping[addr/PGSIZE].addr == 0);
  user_mapping[addr/PGSIZE] = *node;

  uintptr_t sstatus = set_csr(sstatus, SSTATUS_SUM);
  insncpy((void*)addr, uva2kva(addr), PGSIZE);
  write_csr(sstatus, sstatus);

  user_l3pt[addr/PGSIZE] = new_pte;
  flush_page(addr);
}

void handle_trap(trapframe_t* tf)
{
  if (tf->cause == CAUSE_USER_ECALL)
  {
    switch (tf->gpr[17]) {
    case SYSCALL_EXIT:
      do_exit(tf->gpr[10]);
    default:
      for (long i = 1; i < MAX_TEST_PAGES; i++)
        evict(i*PGSIZE);
      do_exit(tf->gpr[10]);
    }
  }
  else if (tf->cause == CAUSE_ILLEGAL_INSTRUCTION)
  {
    assert(tf->epc % 4 == 0);

    int* fssr;
    asm ("jal %0, 1f; fssr x0; 1:" : "=r"(fssr));

    if (*(int*)tf->epc == *fssr)
      do_exit(0); // FP test on non-FP hardware.  "succeed."
    else
      assert(!"illegal instruction");
    tf->epc += 4;
  }
  else if (tf->cause == CAUSE_FETCH_PAGE_FAULT || tf->cause == CAUSE_LOAD_PAGE_FAULT || tf->cause == CAUSE_STORE_PAGE_FAULT)
    handle_fault(tf->badvaddr, tf->cause);
  else
    assert(!"unexpected exception");

  pop_tf(tf);
}

extern uintptr_t _vm_start;
extern uintptr_t _vm_end;

void vm_boot(uintptr_t test_addr)
{
  _Static_assert(SIZEOF_TRAPFRAME_T == sizeof(trapframe_t), "???");

#if (MAX_TEST_PAGES > PTES_PER_PT) || (DRAM_BASE % MEGAPAGE_SIZE) != 0
# error
#endif
  // map user to lowermost megapage
  l1pt[0] = ((pte_t)user_l2pt >> PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  // map kernel to uppermost megapage
#if __riscv_xlen == 64
  l1pt[PTES_PER_PT-1] = ((pte_t)kernel_l2pt >> PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  kernel_l2pt[PTES_PER_PT-1] = (DRAM_BASE/RISCV_PGSIZE << PTE_PPN_SHIFT) | PTE_V | PTE_R | PTE_W | PTE_X | PTE_A | PTE_D;
  user_l2pt[0] = ((pte_t)user_l3pt >> PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  uintptr_t vm_choice = SATP_MODE_SV39;
#else
  l1pt[PTES_PER_PT-1] = (DRAM_BASE/RISCV_PGSIZE << PTE_PPN_SHIFT) | PTE_V | PTE_R | PTE_W | PTE_X | PTE_A | PTE_D;
  uintptr_t vm_choice = SATP_MODE_SV32;
#endif
  write_csr(satp, ((uintptr_t)l1pt >> PGSHIFT) |
                  (vm_choice * (SATP_MODE & ~(SATP_MODE<<1))));

  // map htif memory
#if __riscv_xlen == 64
  kernel_l2pt[0x1fe] = ((pte_t)tohost_l3pt >> PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  tohost_l3pt[0x1ff] = (HTIF_BASE >> PGSHIFT << PTE_PPN_SHIFT) | PTE_V | PTE_R | PTE_W | PTE_A | PTE_D;
#else
  l1pt[0x3fe] = ((pte_t)tohost_l3pt >> PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  tohost_l3pt[0x3ff] = (HTIF_BASE >> PGSHIFT << PTE_PPN_SHIFT) | PTE_V | PTE_R | PTE_W | PTE_A | PTE_D;
#endif

  // Set up PMPs if present, ignoring illegal instruction trap if not.
  uintptr_t pmpc = PMP_NAPOT | PMP_R | PMP_W | PMP_X;
  uintptr_t pmpa = ((uintptr_t)1 << (__riscv_xlen == 32 ? 31 : 53)) - 1;
  asm volatile ("la t0, 1f\n\t"
                "csrrw t0, mtvec, t0\n\t"
                "csrw pmpaddr0, %1\n\t"
                "csrw pmpcfg0, %0\n\t"
                ".align 2\n\t"
                "1:"
                : : "r" (pmpc), "r" (pmpa) : "t0");

  // set up supervisor trap handling
  write_csr(stvec, pa2kva(trap_entry));
  write_csr(sscratch, pa2kva(read_csr(mscratch)));
  write_csr(medeleg,
    (1 << CAUSE_USER_ECALL) |
    (1 << CAUSE_FETCH_PAGE_FAULT) |
    (1 << CAUSE_LOAD_PAGE_FAULT) |
    (1 << CAUSE_STORE_PAGE_FAULT));
  // FPU on; accelerator on; allow supervisor access to user memory access
  write_csr(mstatus, MSTATUS_FS | MSTATUS_XS);
  write_csr(mie, 0);

  freelist_head = pa2kva((void*)&freelist_nodes[0]);
  freelist_tail = pa2kva(&freelist_nodes[MAX_TEST_PAGES-1]);
  pte_t start = ((pte_t)&_vm_start + PGSIZE - 1)/PGSIZE*PGSIZE;
  for (long i = 0; i < MAX_TEST_PAGES; i++)
  {
    freelist_nodes[i].addr = start + (i + 1)*PGSIZE;
    freelist_nodes[i].next = pa2kva(&freelist_nodes[i+1]);
  }
  freelist_nodes[MAX_TEST_PAGES-1].next = 0;

  trapframe_t tf;
  memset(&tf, 0, sizeof(tf));
  uintptr_t sp, gp, tp;
  asm volatile ("mv %0, sp;"
                "mv %1, gp;"
                "mv %2, tp;"
                : "=r"(sp), "=r"(gp), "=r"(tp));
  tf.gpr[2] = sp - DRAM_BASE;
  tf.gpr[3] = gp - DRAM_BASE;
  tf.gpr[4] = tp - DRAM_BASE;
  tf.epc = test_addr - DRAM_BASE;
  pop_tf(&tf);
}