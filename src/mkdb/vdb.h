#ifndef _VDB_H_
#define _VDB_H_

void *vdb_create(int dim);
void vdb_insert(void *_vdb, unsigned char *dna);
int vdb_search(void *_vdb, unsigned char *dna);
void vdb_save(void *_vdb, const char *path);
void vdb_save(void *_vdb, const char *path);
void *vdb_load(const char *path);

#endif
