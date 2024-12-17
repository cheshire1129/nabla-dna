#include "config.h"

#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "dynarray.h"
#include "util.h"
#include "nabla_dna.h"
#include "similarity.h"

#include "vdb.h"

#define DNAS_CHUNKSIZE	16

typedef struct {
	int	resol_rdx, depth_rdx;
	int	resol_dna, depth_dna;
	int	size_rdx, size_dna;
	void	*vdb;
	void *dnas;
} ndb_t;

void
ndb_get_resols(void *_ndb, int *presol_rdx, int *pdepth_rdx, int *presol_dna, int *pdepth_dna)
{
	ndb_t	*ndb = (ndb_t *)_ndb;

	*presol_rdx = ndb->resol_rdx;
	*pdepth_rdx = ndb->depth_rdx;
	*presol_dna = ndb->resol_dna;
	*pdepth_dna = ndb->depth_dna;
}

void *
ndb_create(int resol_rdx, int depth_rdx, int resol_dna, int depth_dna)
{
	ndb_t	*ndb;

	ndb = (ndb_t *)malloc(sizeof(ndb_t));
	if (ndb == NULL)
		return NULL;

	ndb->resol_rdx = resol_rdx;
	ndb->depth_rdx = depth_rdx;
	ndb->resol_dna = resol_dna;
	ndb->depth_dna = depth_dna;
	ndb->size_rdx = get_n_nabla_pixels(resol_rdx);
	ndb->size_dna = get_n_nabla_pixels(resol_dna);
	ndb->vdb = vdb_create(ndb->size_rdx);
	ndb->dnas = dynarray_create(ndb->size_dna, DNAS_CHUNKSIZE);

	return ndb;
}

void
ndb_close(void *_ndb)
{
	ndb_t	*ndb = (ndb_t *)_ndb;

	free(ndb);
}

bool
ndb_insert(void *_ndb, unsigned char *dna_rdx, unsigned char *dna)
{
	ndb_t	*ndb = (ndb_t *)_ndb;

	vdb_insert(ndb->vdb, dna_rdx);
	memcpy(dynarray_add(ndb->dnas), dna, ndb->size_dna);
	return true;
}

static void
store_int(FILE *fp, int value)
{
	fwrite(&value, sizeof(int), 1, fp);
}

static void
store_dnas(FILE *fp, unsigned int size_dna, void *dnas)
{
	unsigned int	count = dynarray_count(dnas);

	store_int(fp, (int)count);
	fwrite(dynarray_to_array(dnas), size_dna, count, fp);
}

bool
ndb_store(void *_ndb, const char *path)
{
	ndb_t	*ndb = (ndb_t *)_ndb;
	char	*path_vdb;
	FILE	*fp;

	fp = fopen(path, "wb");
	if (fp == NULL)
		return false;

	store_int(fp, ndb->resol_rdx);
	store_int(fp, ndb->depth_rdx);
	store_int(fp, ndb->resol_dna);
	store_int(fp, ndb->depth_dna);
	store_int(fp, ndb->size_rdx);
	store_int(fp, ndb->size_dna);

	store_dnas(fp, ndb->size_dna, ndb->dnas);

	fclose(fp);

	path_vdb = path_get_replaced_ext(path, "vdb");
	vdb_save(ndb->vdb, path_vdb);
	free(path_vdb);

	return true;
}

static bool
load_int(FILE *fp, int *pvalue)
{
	if (fread(pvalue, sizeof(int), 1, fp) != 1)
		return false;
	return true;
}

static void *
load_dnas(FILE *fp, unsigned int size_dna)
{
	void	*dnas;
	unsigned int	count;

	if (!load_int(fp, (int *)&count))
		return NULL;
	dnas = dynarray_create(size_dna, DNAS_CHUNKSIZE);
	for (int i = 0; i < count; i++) {
		unsigned char	*pdna = dynarray_add(dnas);
		if (fread(pdna, size_dna, 1, fp) != 1) {
			dynarray_free(dnas);
			return NULL;
		}
	}
	return dnas;
}

void *
ndb_open(const char *path)
{
	ndb_t	*ndb;
	char	*path_vdb;
	FILE	*fp;

	ndb = (ndb_t *)malloc(sizeof(ndb_t));
	if (ndb == NULL)
		return NULL;

	fp = fopen(path, "rb");
	if (fp == NULL)
		return false;

	if (!load_int(fp, &ndb->resol_rdx) ||
	    !load_int(fp, &ndb->depth_rdx) ||
	    !load_int(fp, &ndb->resol_dna) ||
	    !load_int(fp, &ndb->depth_dna) ||
	    !load_int(fp, &ndb->size_rdx) ||
	    !load_int(fp, &ndb->size_dna)) {
		fclose(fp);
		free(ndb);
		return NULL;
	}

	if ((ndb->dnas = load_dnas(fp, ndb->size_dna)) == NULL) {
		fclose(fp);
		free(ndb);
		return NULL;
	}

	fclose(fp);

	path_vdb = path_get_replaced_ext(path, "vdb");
	ndb->vdb = vdb_load(path_vdb);
	free(path_vdb);

	return ndb;
}

int
ndb_search(void *_ndb, float threshold, unsigned char *dna_rdx, unsigned char *dna)
{
	ndb_t	*ndb = (ndb_t *)_ndb;
	unsigned char	*dna_searched;
	double	similarity;
	int	id_dna;

	id_dna = vdb_search(ndb->vdb, dna_rdx);
	dna_searched = dynarray_get(ndb->dnas, id_dna);
	similarity = get_similarity(dna, dna_searched, ndb->size_rdx);
	if (similarity >= threshold)
		return id_dna;
	return -1;
}
