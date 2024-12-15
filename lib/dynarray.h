#ifndef _DYNARRAY_H_
#define _DYNARRAY_H_

#include <stdbool.h>

typedef bool (*dynarray_searcher_t)(void *ptr, void *ctx);
void *dynarray_create(unsigned int size, unsigned int chunksize);
void *dynarray_add(void *dynarray);
void *dynarray_get(void *dynarray, unsigned int idx);
void dynarray_delete(void *dynarray, unsigned int idx);
void dynarray_delete_data(void *dynarray, void *data);
unsigned int dynarray_search(void *dynarray, dynarray_searcher_t searcher, void *ctx);
void dynarray_free(void *dynarray);
void *dynarray_to_array(void *dynarray);
unsigned int dynarray_count(void *dynarray);
void dynarray_clear(void *dynarray);

#endif
