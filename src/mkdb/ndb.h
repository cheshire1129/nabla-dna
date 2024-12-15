#ifndef _NDB_H_
#define _NDB_H_

#include <stdbool.h>

void
ndb_get_sizes(void *ndb, int *psize_rdx, int *psize_dna);

void *
ndb_create(int size_rdx, int size_dna);

void *
ndb_open(const char *path);

bool
ndb_insert(void *ndb, unsigned char *dna_rdx, unsigned char *dna);

int
ndb_search(void *ndb, float threshold, unsigned char *dna_rdx, unsigned char *dna);

void
ndb_close(void *ndb);

bool
ndb_store(void *ndb, const char *path);

#endif
