/*********************************************************************
* Filename:   sha1.h
* Author:     Brad Conte (brad AT bradconte.com)
* Copyright:
* Disclaimer: This code is presented "as is" without any guarantees.
* Details:    Defines the API for the corresponding SHA1 implementation.
*********************************************************************/

#ifndef SHA1_H
#define SHA1_H

#include <stddef.h>
#include <stdint.h>

#define SHA1_BLOCK_SIZE 20              // SHA1 outputs a 20 byte digest

typedef unsigned char uint8_t;             // 8-bit byte
typedef unsigned int  WORD;             // 32-bit word, change to "long" for 16-bit machines

typedef struct _sha1_context_t {
	uint8_t data[64];
	uint32_t datalen;
	unsigned long long bitlen;
	uint32_t state[5];
	uint32_t k[4];
} sha1_context_t;

void Sha1Init(sha1_context_t *ctx);
void Sha1Update(sha1_context_t *ctx, const uint8_t data[], size_t len);
void Sha1Final(sha1_context_t *ctx, uint8_t hash[]);

#endif // SHA1_H
