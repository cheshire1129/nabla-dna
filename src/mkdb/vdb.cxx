#include "config.h"

#include <faiss/IndexHNSW.h>
#include <faiss/index_io.h>

#include <stdlib.h>

typedef struct {
	float	*vec_staged;
	faiss::IndexHNSWFlat	*index;
} vdb_t;

static vdb_t *
new_vdb(faiss::IndexHNSWFlat *index)
{
	vdb_t	*vdb = (vdb_t *)malloc(sizeof(vdb_t));
	vdb->index = index;
	vdb->vec_staged = (float *)malloc(sizeof(float) * index->d);
	return vdb;
}

extern "C" void *
vdb_create(int dim)
{
	faiss::MetricType	metric = faiss::METRIC_L2;
	faiss::IndexHNSWFlat	*index;
	vdb_t	*vdb;

	index = new faiss::IndexHNSWFlat(dim, 30);
	index->hnsw.efConstruction = 40;

	return new_vdb(index);
}

extern "C" void
vdb_insert(void *_vdb, unsigned char *dna)
{
	vdb_t	*vdb = (vdb_t *)_vdb;

	for (int i = 0; i < vdb->index->d; i++)
		vdb->vec_staged[i] = (float)dna[i];
	vdb->index->add(1, vdb->vec_staged);
}

extern "C" int
vdb_search(void *_vdb, unsigned char *dna)
{
	vdb_t	*vdb = (vdb_t *)_vdb;
	float	dist;
	faiss::Index::idx_t	idx;

	for (int i = 0; i < vdb->index->d; i++)
		vdb->vec_staged[i] = (float)dna[i];
	vdb->index->search(1, vdb->vec_staged, 1, &dist, &idx);
	return idx + 1;
}

extern "C" void
vdb_save(void *_vdb, const char *path)
{
	vdb_t	*vdb = (vdb_t *)_vdb;

	faiss::write_index(vdb->index, path);
}

extern "C" void *
vdb_load(const char *path)
{
	faiss::IndexHNSWFlat	*index;

	index = (faiss::IndexHNSWFlat *)faiss::read_index(path);

	return new_vdb(index);
}
