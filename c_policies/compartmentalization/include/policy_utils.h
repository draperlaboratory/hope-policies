#ifndef POLICY_UTILS_H
#define POLICY_UTILS_H
#include <stdlib.h>
#include "policy_meta_set.h"

 #ifdef __cplusplus
extern "C" {
#endif

void print_meta_set(const meta_set_t *meta_set);
int meta_set_to_string(const meta_set_t *meta_set, char *buf, size_t buf_len);
void print_debug(const meta_set_t *ci, const meta_set_t *rs1, const meta_set_t *rs2, const meta_set_t *rs3, const meta_set_t *mem, const meta_set_t *pc);

#ifdef __cplusplus
}
#endif
#endif // POLICY_UTILS_H
