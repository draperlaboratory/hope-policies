#include <stdlib.h>

/*
 * Heap malloc, free wrapper functions
 */

#ifndef DOVER_LIB
#define DOVER_LIB

// Strip tag from a pointer
void* dover_remove_tag(void *ptr);

#endif // DOVER_LIB
