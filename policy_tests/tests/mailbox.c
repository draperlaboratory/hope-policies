#include <stdint.h>
#include <stdio.h>

#include "test_status.h"
#include "test.h"

int test_main(void)
{
	test_positive();

	uint32_t* const PEX_MB = (uint32_t*)0x70000080U;
	uint32_t* const AP_MB = (uint32_t*)0x70000090U;
	uint32_t* const MB_IRQ = (uint32_t*)0x700000a0U;
	printf("Initial PEX mailbox value: %x\n", *PEX_MB);
	uint32_t pex = *PEX_MB;
	*AP_MB = 0x10101010;
	*MB_IRQ = 1;
	while (1) {
		if (pex != *PEX_MB) {
			pex = *PEX_MB;
			if (pex < 0xFFFFFFFFU) {
				printf("Recieved %x from PEX.  Sending %x\n", pex, pex + 0x10101010);
				*AP_MB = pex + 0x10101010;
				*MB_IRQ = 1;
			} else {
				printf("Received %x from PEX.\n", pex);
				break;
			}
		}
	}

	test_pass();
	return test_done();
}
