
#include <stdint.h>
#include <stdbool.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>

#include "policy_eval.h"

#define ALLOC_BUMP_MAX  (KERNEL_MEM_END - (sizeof(meta_set_t)))

// Import global and function definitions
#include "object_defs.h"
#include "func_defs.h"

bool ms_contains(const meta_set_t *ms, const meta_t m)
{
    if (ms == NULL || m > MAX_TAG)
        return false;
    
    int index = m / 32;
    int bit = m % 32;
    uint32_t mask = 1 << bit;
    
    // It would be nice to just return the scrutinee of this if, but it
    if (ms->tags[index] & mask)
        return true;
    else
        return false;
}
void ms_bit_add(meta_set_t *ms, meta_t m)
{
    if (ms == NULL || m > MAX_TAG)
        return;
    
    int index = m / 32;
    int bit = m % 32;
    uint32_t mask = 1 << bit;
    
    ms->tags[index] |= mask;
    return;
}
void ms_bit_remove(meta_set_t *ms, meta_t m)
{
    if (ms == NULL || m > MAX_TAG)
        return;
    
    int index = m / 32;
    int bit = m % 32;
    uint32_t mask = ~(1 << bit);
    
    ms->tags[index] &= mask;
    return;
}
bool ms_eq(const meta_set_t *ms1, const meta_set_t *ms2)
{
    if (ms1 == ms2)
        return true;
    else if (ms1 == 0 || ms2 == 0)
        return false;
    else
        for (int i = 0; i < META_SET_WORDS; i++) {
            if (ms1->tags[i] != ms2->tags[i])
                return false;
        }
    return true;
}
int ms_union(meta_set_t *ms1, const meta_set_t *ms2)
{
    if (ms1 == NULL || ms2 == NULL)
        return -1;
    for (int i = 0; i < META_SET_WORDS; i++) {
        if (((i >= META_SET_BITFIELDS && ms1->tags[i]) && ms2->tags[i]) && ms1->tags[i] !=
            ms2->tags[i])
            return i;
        else
            ms1->tags[i] |= ms2->tags[i];
    }
    return 0;
}
