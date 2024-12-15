#include "config.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dynarray.h"

#define DYNARRAY_DEFAULT_ALLOCCHUNK	16

typedef struct {
	unsigned int	count, alloced, chunksize;
	unsigned int	unitsize;
	void	*data;
} dynarray_t;

void *
dynarray_create(unsigned int size, unsigned int chunksize)
{
	dynarray_t	*dynarr = NULL;

	if (size == 0)
		return NULL;
	if (chunksize == 0)
		chunksize = DYNARRAY_DEFAULT_ALLOCCHUNK;
	dynarr = (dynarray_t *)malloc(sizeof(dynarray_t));
	if (dynarr == NULL)
		return NULL;
	dynarr->count = 0;
	dynarr->alloced = chunksize;
	dynarr->chunksize = chunksize;
	dynarr->unitsize = size;
	dynarr->data = malloc(size * chunksize);
	if (dynarr->data == NULL) {
		free(dynarr);
		return NULL;
	}
	return dynarr;
}

void *
dynarray_add(void *dynarray)
{
	dynarray_t	*dynarr = (dynarray_t *)dynarray;

	if (dynarr->count == dynarr->alloced) {
		dynarr->data = realloc(dynarr->data, dynarr->unitsize * (dynarr->alloced + dynarr->chunksize));
		if (dynarr->data == NULL)
			return NULL;

		dynarr->alloced += dynarr->chunksize;
	}
	dynarr->count++;
	return (char *)dynarr->data + (dynarr->count - 1) * dynarr->unitsize;
}

void
dynarray_free(void *dynarray)
{
	dynarray_t	*dynarr = (dynarray_t *)dynarray;

	if (dynarr) {
		free(dynarr->data);
		free(dynarr);
	}
}

void *
dynarray_get(void *dynarray, unsigned int idx)
{
	dynarray_t	*dynarr = (dynarray_t *)dynarray;

	if (dynarr && idx >= 1 && idx <= dynarr->count) {
		return (char *)dynarr->data + (idx - 1) * dynarr->unitsize;
	}
	return NULL;
}

void
dynarray_delete(void *dynarray, unsigned int idx)
{
	dynarray_t	*dynarr = (dynarray_t *)dynarray;

	if (dynarr == NULL || idx > dynarr->count)
		return;

	if (idx > 0 && idx < dynarr->count) {
		unsigned int	offset = ((idx - 1) * dynarr->unitsize);
		unsigned int	length = (dynarr->count - idx) * dynarr->unitsize;

		memmove((char *)dynarr->data + offset, (char *)dynarr->data + offset + dynarr->unitsize, length);
	}
	dynarr->count--;
}

void
dynarray_delete_data(void *dynarray, void *data)
{
	dynarray_t	*dynarr = (dynarray_t *)dynarray;

	if (dynarr == NULL || data == NULL)
		return;

	if (data >= dynarr->data) {
		unsigned int	idx = (unsigned int)(((char *)data - (char *)dynarr->data)) / dynarr->unitsize + 1;
		dynarray_delete(dynarray, idx);
	}
}

unsigned int
dynarray_search(void *dynarray, dynarray_searcher_t searcher, void *ctx)
{
	dynarray_t	*dynarr = (dynarray_t *)dynarray;

	if (dynarr != NULL || searcher != NULL) {
		char	*p;
		unsigned int	i;

		for (i = 0, p = (char *)dynarr->data; i < dynarr->count; p += dynarr->unitsize, i++) {
			if (searcher(p, ctx))
				return (i + 1);
		}
	}
	return 0;
}

void *
dynarray_to_array(void *dynarray)
{
	dynarray_t	*dynarr = (dynarray_t *)dynarray;

	if (dynarr)
		return dynarr->data;
	return NULL;
}

void
dynarray_clear(void *dynarray)
{
	dynarray_t	*dynarr = (dynarray_t *)dynarray;

	if (dynarr) {
		free(dynarr->data);
		dynarr->data = NULL;
		dynarr->count = 0;
		dynarr->alloced = 0;
	}
}

unsigned int
dynarray_count(void *dynarray)
{
	dynarray_t	*dynarr = (dynarray_t *)dynarray;
	if (dynarr)
		return dynarr->count;
	return 0;
}
