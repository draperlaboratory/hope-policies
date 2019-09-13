# Dhrystone Test

This test was taken from the Xilinx Zynq7000 baremetal test examples. The number of loops
can be changed in the `common.mk` file by changing the value of the `-DDHRY_LOOPS`
variable.

Please note that this test uses a larger than normal bss section as provided by the linker
script. This is meant to work with a qemu instance that also has a larger RAM than what is
emulated on the HiFIVE model.

# Running

To run this test from in the test framework, run the make command from the root test
directory

``` sh
make dhrystone
```

The output will be in `output/isp-run-dhrystone-osv.bare.main.$POLICY/uart.log`. This is
where you can see the Dhrystone score.

# Debugging

After building the test with the test framework make command you can interact with the
test using the `isp_run_app` command:

```
isp_run_app /repos/policies/policy_tests/build/bare/dhrystone \
            --policy /repos/policies/policy_tests/kernels/osv.bare.main.none-debug \
            --simulator qemu \
            --runtime bare \
            --gdb 1234 \
            --uart \
            --output /repos/policies/policy_tests/output
```

Then in another window you can connect via GDB in one of two ways:

With a regular gdb command, where you can add `-ex` arguments:
```
riscv32-unknown-elf-gdb -ex "set riscv use-compressed-breakpoints off" \
                        -ex "target remote :1234" \
                        /repos/policies/policy_tests/build/bare/dhrystone
```

or using the `isp_debug` script:
```
isp_debug -s qemu /repos/policies/policy_tests/build/bare/dhrystone 1234
```
