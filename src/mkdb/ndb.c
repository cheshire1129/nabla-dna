#include "config.h"

#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "dynarray.h"
#include "nabla_dna.h"
#include "similarity.h"

#define DNAS_CHUNKSIZE	16

typedef struct _node {
	unsigned char	dna_byte;
	struct _node	*children[256];
	void *id_dnas;
} rdx_node_t;

typedef struct {
	int	resol_rdx, depth_rdx;
	int	resol_dna, depth_dna;
	int	size_rdx, size_dna;
	int	n_children;
	rdx_node_t	*root;
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

static rdx_node_t *
create_node(unsigned char dna_byte, int n_children)
{
	rdx_node_t	*node;

	node = (rdx_node_t *)malloc(sizeof(rdx_node_t));
	if (node == NULL)
		return NULL;

	node->dna_byte = dna_byte;
	for (int i = 0; i < n_children; i++)
		node->children[i] = NULL;
	node->id_dnas = dynarray_create(sizeof(int), DNAS_CHUNKSIZE);
	return node;
}

static void
free_node(rdx_node_t *node, int n_children)
{
	if (node == NULL)
		return;
	for (int i = 0; i < n_children; i++) {
		free_node(node->children[i], n_children);
	}
	dynarray_free(node->id_dnas);
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
	ndb->n_children = 2 << ndb->depth_rdx;
	ndb->root = create_node(0, ndb->n_children);
	ndb->dnas = dynarray_create(ndb->size_dna, DNAS_CHUNKSIZE);

	return ndb;
}

void
ndb_close(void *_ndb)
{
	ndb_t	*ndb = (ndb_t *)_ndb;

	free_node(ndb->root, ndb->n_children);
	free(ndb);
}

bool
ndb_insert(void *_ndb, unsigned char *dna_rdx, unsigned char *dna)
{
	ndb_t	*ndb = (ndb_t *)_ndb;
	rdx_node_t	*cur = ndb->root;
	unsigned int	id_dna;

	for (int i = 0; i < ndb->size_rdx; i++) {
		unsigned char	dbyte = dna_rdx[i];

		if (cur->children[dbyte] == NULL) {
			cur->children[dbyte] = create_node(dbyte, ndb->n_children);
			if (cur->children[dbyte] == NULL)
				return false;
		}
		cur = cur->children[dbyte];
	}

	memcpy(dynarray_add(ndb->dnas), dna, ndb->size_dna);
	id_dna = dynarray_count(ndb->dnas);
	memcpy(dynarray_add(cur->id_dnas), &id_dna, sizeof(int));
	return true;
}

static void
store_byte(FILE *fp, unsigned char byte)
{
	fwrite(&byte, sizeof(unsigned char), 1, fp);
}

static void
store_int(FILE *fp, int value)
{
	fwrite(&value, sizeof(int), 1, fp);
}

static void
store_id_dnas(FILE *fp, void *id_dnas)
{
	unsigned int	count = dynarray_count(id_dnas);

	store_int(fp, (int)count);
	fwrite(dynarray_to_array(id_dnas), sizeof(int), count, fp);
}

static void
store_node(FILE *fp, ndb_t *ndb, int level, rdx_node_t *node)
{
	if (node == NULL) {
		store_byte(fp, 0);
		return;
	}
	store_byte(fp, 1);
	store_byte(fp, node->dna_byte);
	if (level < ndb->size_rdx) {
		for (int i = 0; i < ndb->n_children; i++) {
			store_node(fp, ndb, level + 1, node->children[i]);
		}
	}
	else {
		store_id_dnas(fp, node->id_dnas);
	}
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

	store_node(fp, ndb, 0, ndb->root);
	store_dnas(fp, ndb->size_dna, ndb->dnas);

	fclose(fp);
	return true;
}

static bool
load_byte(FILE *fp, unsigned char *pbyte)
{
	if (fread(pbyte, sizeof(unsigned char), 1, fp) != 1)
		return false;
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
load_id_dnas(FILE *fp)
{
	void	*id_dnas;
	unsigned int	count;

	if (!load_int(fp, (int *)&count))
		return NULL;
	id_dnas = dynarray_create(sizeof(int), DNAS_CHUNKSIZE);
	for (int i = 0; i < count; i++) {
		unsigned int	*pid_dna = dynarray_add(id_dnas);
		if (fread(pid_dna, sizeof(int), 1, fp) != 1) {
			dynarray_free(id_dnas);
			return NULL;
		}
	}
	return id_dnas;
}

bool
load_node(FILE *fp, ndb_t *ndb, int level, rdx_node_t **pnode)
{
	rdx_node_t	*node;
	unsigned char	valid;
	unsigned char	dna_byte;

	if (!load_byte(fp, &valid))
		return false;
	if (!valid) {
		*pnode = NULL;
		return true;
	}

	if (!load_byte(fp, &dna_byte))
		return false;
	node = create_node(dna_byte, ndb->n_children);
	if (node == NULL)
		return false;

	if (level < ndb->size_rdx) {
		for (int i = 0; i < ndb->n_children; i++) {
			if (!load_node(fp, ndb, level + 1, &node->children[i])) {
				free_node(node, ndb->n_children);
				return false;
			}
		}
	}
	else {
		node->id_dnas = load_id_dnas(fp);
		if (node->id_dnas == NULL) {
			free_node(node, ndb->n_children);
			return false;
		}
	}
	*pnode = node;
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

	ndb->n_children = 2 << ndb->depth_rdx;

	if (!load_node(fp, ndb, 0, &ndb->root)) {
		fclose(fp);
		free(ndb);
		return NULL;
	}

	if ((ndb->dnas = load_dnas(fp, ndb->size_dna)) == NULL) {
		fclose(fp);
		free_node(ndb->root, ndb->n_children);
		free(ndb);
		return NULL;
	}

	fclose(fp);
	return ndb;
}

int
ndb_search(void *_ndb, float threshold, unsigned char *dna_rdx, unsigned char *dna)
{
	ndb_t	*ndb = (ndb_t *)_ndb;
	rdx_node_t	*cur = ndb->root;
	int	id_dna_best = -1;
	double	similarity_best = -1;
	unsigned int	count;

	for (int i = 0; i < ndb->size_rdx; i++) {
		unsigned char	dbyte = dna_rdx[i];

		if (cur->children[dbyte] == NULL)
			return -1;
		cur = cur->children[dbyte];
	}

	count = dynarray_count(cur->id_dnas);
	for (int i = 0; i < count; i++) {
		unsigned int	id_dna;
		double	similarity;
		unsigned char	*dna_db;

		id_dna = *(unsigned int *)dynarray_get(cur->id_dnas, i + 1);
		dna_db = (unsigned char *)dynarray_get(ndb->dnas, id_dna);
		similarity = cosine_similarity(dna, dna_db, ndb->size_dna);
		if (similarity >= threshold && similarity > similarity_best) {
			id_dna_best = id_dna;
			similarity_best = similarity;
		}
	}

	return id_dna_best;
}
