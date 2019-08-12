# MiBench2

MiBench is an embedded benchmark suite which can be found at [eecs.umich.edu/mibench].

MiBench2 includes additional tests designed for IoT devices, and can be found at [https://github.com/impedimentToProgress/MiBench2].

This test suite includes tests from MiBench2, modified to run within the ISP test framework.

## Building

To build and run the MiBench tests, run `make TESTS=mibench` from the `policies/policy-tests` directory. The tests can also be run with different configurations, such as a FreeRTOS runtime or different policies.

## Test Status

- Adpcm_decode: ported
- Adpcm_encode: ported
- AES: ported
- Basicmath: WIP
- Bitcount: ported
- Blowfish: WIP
- CRC: ported
- Dijkstra: ported
- FFT: WIP
- Limits: WIP
- Lzfx: WIP
- Overflow: not ported, ARM standards test
- Patricia: not ported, runtime errors
- Picojpeg: WIP
- Qsort: ported
- Randmath: WIP
- RC4: ported
- Regress: not ported, ARM standards test
- RSA: ported
- SHA: ported
- Stringsearch: WIP
- Susan: not ported, runtime errors
- VCFlags: not ported, ARM standards test