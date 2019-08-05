.globl ROR
.type ROR, @function
ROR:
    addi sp,sp,-16
    andi t1,a1,0xff     # ARM shifts by the least significant byte
    neg t1,t1
    sll t0,a0,t1
    srl a0,a0,a1
    or a0,a0,t0
    addi sp,sp,16
    ret


.globl ROR_FLAG
.type ROR_FLAG, @function
ROR_FLAG:
    addi sp,sp,-16
    mv t0,a0
    mv a0,x0            # Clear all flags
    andi t1,a1,0xff     # ARM shifts by the least significant byte
    beqz t1,SET_Z_FLAG  # If the shift value == 0, no changes are made
    neg t2,t1
    sll t3,t0,t2
    srl t0,t0,t1
    or t0,t0,t3
    srl a0,t0,31        # Set carry flag if first bit is set
    j SET_Z_FLAG


.globl LSR
.type LSR, @function
LSR:
    addi sp,sp,-16
    andi t0,a1,0xff     # ARM shifts by the least significant byte
    li t1,32
    bgeu t0,t1,LSR1     # If the shift value >= 32, the result is cleared
    srl a0,a0,t0
    addi sp,sp,16
    ret
LSR1:
    mv a0,x0
    addi sp,sp,16
    ret


.globl LSR_FLAG
.type LSR_FLAG, @function
LSR_FLAG:
    addi sp,sp,-16
    mv t0,a0
    mv a0,x0            # Clear all flags
    andi t1,a1,0xff     # ARM shifts by the least significant byte
    li t2,32
    # If the shift value > 32, the result is cleared and the carry bit is clear
    bgtu t1,t2,CLEAR_RESULT
    beqz t1,SET_Z_FLAG  # If the shift value == 0, no changes are made

    addi t1,t1,-1
    srl t0,t0,t1        # Perform all but the last shift
    andi a0,t0,1        # Set carry flag if last bit is set
    srl t0,t0,1         # Perform the last shift
    j SET_Z_FLAG


.globl LSL
.type LSL, @function
LSL:
    addi sp,sp,-16
    andi t0,a1,0xff     # ARM shifts by the least significant byte
    li t1,32
    bgeu t0,t1,LSL1     # If the shift value >= 32, the result is cleared
    sll a0,a0,t0
    addi sp,sp,16
    ret
LSL1:
    mv a0,x0
    addi sp,sp,16
    ret


.globl LSL_FLAG
.type LSL_FLAG, @function
LSL_FLAG:
    addi sp,sp,-16
    mv t0,a0
    mv a0,x0            # Clear all flags
    andi t1,a1,0xff     # ARM shifts by the least significant byte
    li t2,32
    # If the shift value > 32, the result is cleared and the carry bit is clear
    bgtu t1,t2,CLEAR_RESULT
    beqz t1,SET_Z_FLAG  # If the shift value == 0, no changes are made

    addi t1,t1,-1
    sll t0,t0,t1        # Perform all but the last shift
    srl a0,t0,31        # Set carry flag if first bit is set
    sll t0,t0,1         # Perform the last shift
    j SET_Z_FLAG


CLEAR_RESULT:
    mv t0,x0
SET_Z_FLAG:
    bne t0,x0,SET_N_FLAG
    ori a0,a0,2
SET_N_FLAG:
    bgez t0,RETURN_FLAGS
    ori a0,a0,4
RETURN_FLAGS:
    addi sp,sp,16
    ret
