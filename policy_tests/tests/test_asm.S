   .globl read_mxl

read_mxl:
   csrr t0, 0x301
   bgez t0, rv32
   slli t0, t0, 1
   bgez t0, rv64
   li   a0, 128
   j    rv_out
rv32:
   li   a0, 32
   j    rv_out
rv64:
   li   a0, 64
rv_out:
   ret
