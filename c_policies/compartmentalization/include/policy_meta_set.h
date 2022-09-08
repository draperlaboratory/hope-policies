#ifndef META_SET_H
#define META_SET_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif
// The size of a whole tag set, in uint32s
#define META_SET_WORDS 5

// The number of bitfields in ms->tags
#define META_SET_BITFIELDS 2

// The number of tag argument postions following the bitfields in ms->tags
#define META_SET_ARGS 3

// Arg1 = Subject ID on code, Object ID for globals
// Arg2 = Heap Cell Color
// Arg3 = Heap Pointer Color

// The maximum tag.  Tags are positions in the 'tags' bitfield.
// With two words for bitfields, 64 is logical max before we need to
// redesign the meta set
#define MAX_TAG 58

typedef uintptr_t meta_t;
typedef struct {
  uint32_t tags[META_SET_WORDS];
} meta_set_t;
  
bool ms_contains(const meta_set_t *ms, meta_t m);
bool ms_eq(const meta_set_t *ms1, const meta_set_t *ms2);
void ms_bit_add(meta_set_t *ms, meta_t m);
void ms_bit_remove(meta_set_t *ms, meta_t m);
int ms_union(meta_set_t *ms1, const meta_set_t *ms2);

extern const char * func_defs[];
extern const char * object_defs[];

#ifdef __cplusplus
}
#endif
#endif
