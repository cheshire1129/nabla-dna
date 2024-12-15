#ifndef _NDB_H_
#define _NDB_H_

#include <stdbool.h>

void
ndb_get_resols(void *ndb, int *presol_rdx, int *pdepth_rdx, int *presol_dna, int *pdepth_dna);

void *
ndb_create(int resol_rdx, int depth_rdx, int resol_dna, int depth_dna);

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
