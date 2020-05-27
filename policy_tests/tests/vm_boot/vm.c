#include <unistd.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "bsp/encoding.h"

#define MAX_TEST_PAGES 255

typedef unsigned long pte_t;
#define LEVELS (sizeof(pte_t) == sizeof(uint64_t) ? 3 : 2)
#define PTIDXBITS (RISCV_PGSHIFT - (sizeof(pte_t) == 8 ? 3 : 2))
#define VPN_BITS (PTIDXBITS * LEVELS)
#define VA_BITS (VPN_BITS + RISCV_PGSHIFT)
#define PTES_PER_PT (1UL << RISCV_PGLEVEL_BITS)
#define MEGAPAGE_SIZE (PTES_PER_PT * RISCV_PGSIZE)

typedef struct
{
  uintptr_t gpr[32];
  uintptr_t sr;
  uintptr_t epc;
  uintptr_t badvaddr;
  uintptr_t cause;
} trapframe_t;

void trap_entry(void);
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
#define uva2pa(uva) ((void*)(uva) + DRAM_BASE)

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
# define NPT 7
#define kernel_l2pt pt[2]
# define user_l3pt pt[3]
#define tohost_l3pt pt[4]
#define phys_l2pt pt[5]
#define phys_l3pt pt[6]
#else
# define NPT 3
# define user_l3pt user_l2pt
#define tohost_l3pt pt[2]
#endif
pte_t pt[NPT][PTES_PER_PT] __attribute__((aligned(RISCV_PGSIZE)));

typedef struct { pte_t addr; void* next; } freelist_t;

freelist_t user_mapping[MAX_TEST_PAGES];
freelist_t freelist_nodes[MAX_TEST_PAGES];
freelist_t *freelist_head, *freelist_tail;

static void evict(unsigned long addr)
{
  assert(addr >= RISCV_PGSIZE && addr < MAX_TEST_PAGES * RISCV_PGSIZE);
  addr = addr/RISCV_PGSIZE*RISCV_PGSIZE;

  freelist_t* node = &user_mapping[addr/RISCV_PGSIZE];
  if (node->addr)
  {
    // check accessed and dirty bits
    assert(user_l3pt[addr/RISCV_PGSIZE] & PTE_A);
    uintptr_t sstatus = set_csr(sstatus, SSTATUS_SUM);
    if (memcmp((void*)addr, uva2kva(addr), RISCV_PGSIZE)) {
      assert(user_l3pt[addr/RISCV_PGSIZE] & PTE_D);
      memcpy((void*)addr, uva2kva(addr), RISCV_PGSIZE);
    }
    write_csr(sstatus, sstatus);

    user_mapping[addr/RISCV_PGSIZE].addr = 0;

    if (freelist_tail == 0)
      freelist_head = freelist_tail = node;
    else
    {
      freelist_tail->next = node;
      freelist_tail = node;
    }
  }
}

void* __attribute__((noinline)) insncpy(void* dest, const void* src, size_t n)
{
  uint32_t* insn_dest = (uint32_t*)dest;
  uint32_t* insn_src = (uint32_t*)src;
  for (size_t i = 0; i < n/sizeof(uint32_t); i++)
    insn_dest[i] = insn_src[i];
  return dest;
}

void handle_fault(uintptr_t addr, uintptr_t cause)
{
  assert(addr >= RISCV_PGSIZE && addr < MAX_TEST_PAGES * RISCV_PGSIZE);
  addr = addr/RISCV_PGSIZE*RISCV_PGSIZE;

  if (user_l3pt[addr/RISCV_PGSIZE]) {
    if (!(user_l3pt[addr/RISCV_PGSIZE] & PTE_A)) {
      user_l3pt[addr/RISCV_PGSIZE] |= PTE_A;
    } else {
      assert(!(user_l3pt[addr/RISCV_PGSIZE] & PTE_D) && cause == CAUSE_STORE_PAGE_FAULT);
      user_l3pt[addr/RISCV_PGSIZE] |= PTE_D;
    }
    flush_page(addr);
    return;
  }

  freelist_t* node = freelist_head;
  assert(node);
  freelist_head = node->next;
  if (freelist_head == freelist_tail)
    freelist_tail = 0;

  uintptr_t new_pte = (node->addr >> RISCV_PGSHIFT << PTE_PPN_SHIFT) | PTE_V | PTE_U | PTE_R | PTE_W | PTE_X;
  user_l3pt[addr/RISCV_PGSIZE] = new_pte | PTE_A | PTE_D;
  flush_page(addr);

  assert(user_mapping[addr/RISCV_PGSIZE].addr == 0);
  user_mapping[addr/RISCV_PGSIZE] = *node;

  uintptr_t sstatus = set_csr(sstatus, SSTATUS_SUM);
  insncpy((void*)addr, uva2kva(addr), RISCV_PGSIZE);
  write_csr(sstatus, sstatus);

  user_l3pt[addr/RISCV_PGSIZE] = new_pte;
  flush_page(addr);

  asm volatile("fence.i");
}

void handle_trap(trapframe_t* tf)
{
  if (tf->cause == CAUSE_USER_ECALL)
  {
    switch (tf->gpr[17]) {
    case SYSCALL_WRITE:
      // Repeat the write system call to machine mode for direct physical memory access
      tf->gpr[10] = (uintptr_t)(write((int)tf->gpr[10], (const void*)uva2pa(tf->gpr[11]), (size_t)tf->gpr[12]));
      tf->epc += 4; // tf->epc points to ecall
      break;
    case SYSCALL_EXIT:
      do_exit(tf->gpr[10]);
    default:
      for (long i = 1; i < MAX_TEST_PAGES; i++)
        evict(i*RISCV_PGSIZE);
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

extern uintptr_t _stack;
extern uintptr_t _vm_start;
extern uintptr_t _vm_end;

void vm_boot(uintptr_t test_addr)
{
#if (MAX_TEST_PAGES > PTES_PER_PT)
# error too many test pages
#elif (DRAM_BASE % MEGAPAGE_SIZE) != 0
# error megapage is not aligned to DRAM base
#endif
  // map user to lowermost megapage
  l1pt[0] = ((pte_t)user_l2pt >> RISCV_PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  // map kernel to uppermost megapage
#if __riscv_xlen == 64
  l1pt[PTES_PER_PT-1] = ((pte_t)kernel_l2pt >> RISCV_PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  kernel_l2pt[PTES_PER_PT-1] = (DRAM_BASE/RISCV_PGSIZE << PTE_PPN_SHIFT) | PTE_V | PTE_R | PTE_W | PTE_X | PTE_A | PTE_D;
  user_l2pt[0] = ((pte_t)user_l3pt >> RISCV_PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  uintptr_t vm_choice = SATP_MODE_SV39;
#else
  l1pt[PTES_PER_PT-1] = (DRAM_BASE/RISCV_PGSIZE << PTE_PPN_SHIFT) | PTE_V | PTE_R | PTE_W | PTE_X | PTE_A | PTE_D;
  uintptr_t vm_choice = SATP_MODE_SV32;
#endif
  write_csr(satp, ((uintptr_t)l1pt >> RISCV_PGSHIFT) |
                  (vm_choice * (SATP_MODE & ~(SATP_MODE<<1))));

  // map htif memory
#if __riscv_xlen == 64
  kernel_l2pt[0x1fe] = ((pte_t)tohost_l3pt >> RISCV_PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  tohost_l3pt[0x1ff] = (HTIF_BASE >> RISCV_PGSHIFT << PTE_PPN_SHIFT) | PTE_V | PTE_R | PTE_W | PTE_A | PTE_D;
#else
  l1pt[0x3fe] = ((pte_t)tohost_l3pt >> RISCV_PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  tohost_l3pt[0x3ff] = (HTIF_BASE >> RISCV_PGSHIFT << PTE_PPN_SHIFT) | PTE_V | PTE_R | PTE_W | PTE_A | PTE_D;
#endif

  // map hard-coded physical page 0xc0080000 so that the virtual address and physical address there are the same
  // because a subroutine of printf loads a hard-coded address in that page from memory and accesses it
  pte_t phys_vpn[3] = {
    DRAM_BASE >> (RISCV_PGSHIFT + 2*RISCV_PGLEVEL_BITS),
    0x000,
    0x080
  };
  l1pt[phys_vpn[0]] = ((pte_t)phys_l2pt >> RISCV_PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  phys_l2pt[phys_vpn[1]] = ((pte_t)phys_l3pt >> RISCV_PGSHIFT << PTE_PPN_SHIFT) | PTE_V;
  phys_l3pt[phys_vpn[2]] = ((pte_t)((DRAM_BASE >> RISCV_PGSHIFT) + phys_vpn[2]) << PTE_PPN_SHIFT) | PTE_V | PTE_U | PTE_R | PTE_W | PTE_A | PTE_D;


  // Set up PMPs if present
  uintptr_t pmpc = PMP_NAPOT | PMP_R | PMP_W | PMP_X;
  uintptr_t pmpa = ((uintptr_t)1 << (__riscv_xlen == 32 ? 31 : 53)) - 1;
  write_csr(pmpaddr0, pmpa);
  write_csr(pmpcfg0, pmpc);

  // set up supervisor trap handling
  write_csr(stvec, pa2kva(trap_entry));
  write_csr(sscratch, pa2kva(read_csr(mscratch) - RISCV_PGSIZE));
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
  pte_t start = ((pte_t)&_vm_start + RISCV_PGSIZE - 1)/RISCV_PGSIZE*RISCV_PGSIZE;
  for (long i = 0; i < MAX_TEST_PAGES; i++)
  {
    freelist_nodes[i].addr = start + (i + 1)*RISCV_PGSIZE;
    freelist_nodes[i].next = pa2kva(&freelist_nodes[i+1]);
  }
  freelist_nodes[MAX_TEST_PAGES-1].next = 0;

  trapframe_t tf;
  memset(&tf, 0, sizeof(tf));
  tf.gpr[2] = (read_csr(mscratch) - 2*RISCV_PGSIZE) - DRAM_BASE;
  tf.epc = test_addr - DRAM_BASE;
  pop_tf(&tf);
}