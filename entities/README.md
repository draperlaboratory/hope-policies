A Guide to Entities
===================

List of all known entities
--------------------------

Hardware Entities
=================

ISA
---

ISA.RISCV.Reg.Env
ISA.RISCV.Reg.Default
ISA.RISCV.Reg.RZero

ISA.RISCV.CSR.Default
ISA.RISCV.CSR.MTVec

SOC
---

SOC.Memory.Flash_0

SOC.Memory.Ram_0

SOC.IO.UART_0
SOC.IO.UART_1
SOC.IO.UART_2
SOC.IO.UART_3

SOC.Timer.MTIME
SOC.Timer.MTIME_CMP

Software Entities
=================

Code
----

Code.FRTOS.dover_ptr_tag
Code.FRTOS.dover_ptr_untag
Code.FRTOS.dover_ptr_zero
Code.FRTOS.dover_remove_tag
Code.FRTOS.dover_tag
Code.FRTOS.dover_untag
Code.FRTOS.pvPortMalloc

Data
----

Data.Global.ucHeap

Tools
-----

Tools.Elf.Section.SHF_ALLOC
Tools.Elf.Section.SHF_EXECINSTR
Tools.Elf.Section.SHF_WRITE

Tools.GCC.Analysis.CFI_Target
    
Tools.Newlib._vfprintf_r
Tools.Newlib.longjmp
Tools.Newlib.memcpy

Tools.Link.MemoryMap.Default
Tools.Link.MemoryMap.UserHeap
Tools.Link.MemoryMap.UserStack
