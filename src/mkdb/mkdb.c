#include "config.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>

#include "util.h"
#include "dynarray.h"
#include "ndb.h"
#include "nabla_dna.h"

static bool	insert_mode = false;
static int	resol_rdx = 2;
static int	resol_dna = 4;
static int	depth_rdx = 2;
static int	depth_dna = 8;
static float	threshold = -1;
static const char	*inpath;
static const char	*img_folder;
static const char	*path_ndb;
static void	*ndb;

static void
usage(void)
{
	printf(
"Usage: mkdb [<options>] <image name/path/folder or list file>\n"
"   <options>\n"
"   -h: help(this message)\n"
"   -I <image folder>: image folder(env var: IMAGE_FOLDER)\n"
"   -A: DNA insert mode\n"
"   -x <dna resolution>: dna resolutions of an indexed dna and stored one\n"
"              default: 2(indexing) 4(stored). Must precede the -D option\n"
"              format: indexed:stored\n"
"   -e <dna depth>: dna depth(default: 2:8)\n"
"   -d <dna db>: existing dna db\n"
"   -D <dna db>: newly created dna db\n"
"   -t <threshold>: threshold for search DNA\n"
		);
}

static void
setup_env(void)
{
	img_folder = getenv("IMAGE_FOLDER");
}

static void
parse_args(int argc, char *argv[])
{
        int     c;

        while ((c = getopt(argc, argv, "hI:Ax:e:d:D:t:")) != -1) {
                switch (c) {
		case 'I':
			img_folder = optarg;
			break;
		case 'A':
			insert_mode = true;
			break;
                case 'x':
                        if (sscanf(optarg, "%d:%d", &resol_rdx, &resol_dna) != 2) {
                                usage();
                                exit(1);
                        }
                        break;
                case 'e':
                        if (sscanf(optarg, "%d:%d", &depth_rdx, &depth_dna) != 2) {
                                usage();
                                exit(1);
                        }
                        break;
		case 'D':
			if ((ndb = ndb_create(resol_rdx, depth_rdx, resol_dna, depth_dna)) == NULL) {
				errmsg("can't create ndb: %s\n", optarg);
				exit(2);
			}
			path_ndb = optarg;
			break;
		case 'd':
			path_ndb = optarg;
			if ((ndb = ndb_open(path_ndb)) == NULL) {
				errmsg("can't open ndb: %s\n", optarg);
				exit(2);
			}
			ndb_get_resols(ndb, &resol_rdx, &depth_rdx, &resol_dna, &depth_dna);
			break;
		case 't':
			if (sscanf(optarg, "%f", &threshold) != 1) {
				usage();
				exit(1);
			}
			break;
                case 'h':
                        usage();
                        exit(0);
                default:
			errmsg("invalid option");
			usage();
			exit(1);
		}
	}
	if (argc - optind < 1) {
		usage();
		exit(1);
	}
	if (ndb == NULL) {
		errmsg("No nabla DB");
		exit(1);
	}
	inpath = argv[optind];
}

static bool
extract_imgpath(const char *imgpath, dnabla_t **pdnabla, dnabla_t **pdnabla_rdx)
{
	ibmp_t	*ibmp;

	ibmp = ibmp_load(imgpath);
	if (ibmp == NULL) {
		errmsg("failed to load: %s", imgpath);
		return false;
	}

	*pdnabla_rdx = build_nabla_dna(ibmp, resol_rdx, depth_rdx);
	*pdnabla = build_nabla_dna(ibmp, resol_dna, depth_dna);
	ibmp_free(ibmp);

	return true;
}

typedef struct {
	dnabla_t *dnabla, *dnabla_rdx;
} extract_img_ctx_t;

static bool
func_extract_img(const char *imgpath, void *ctx)
{
	extract_img_ctx_t	*pctx = (extract_img_ctx_t *)ctx;

	return extract_imgpath(imgpath, &pctx->dnabla, &pctx->dnabla_rdx);
}

static bool
extract_img(const char *imgname, dnabla_t **pdnabla, dnabla_t **pdnabla_rdx)
{
	extract_img_ctx_t	ctx;

	if (!try_iter_imgfmts(img_folder, imgname, func_extract_img, &ctx))
		return false;
	*pdnabla = ctx.dnabla;
	*pdnabla_rdx = ctx.dnabla_rdx;
	return true;
}

typedef struct {
	void *dynarr_dnabla, *dynarr_dnabla_rdx;
} extract_list_ctx_t;

static bool
func_extract_list(unsigned int idx, const char *img_name, void *ctx)
{
	dnabla_t	*dnabla, *dnabla_rdx;
	extract_list_ctx_t	*pctx = (extract_list_ctx_t *)ctx;

	if (!extract_img(img_name, &dnabla, &dnabla_rdx))
		return false;
	*(dnabla_t **)dynarray_add(pctx->dynarr_dnabla) = dnabla;
	*(dnabla_t **)dynarray_add(pctx->dynarr_dnabla_rdx) = dnabla_rdx;
	return true;
}

static int
extract_img_list(const char *path_list, void **pdynarr_dnabla, void **pdynarr_dnabla_rdx)
{
	extract_list_ctx_t	ctx;
	void	*dynarr_dnabla, *dynarr_dnabla_rdx;
	int	count;

	dynarr_dnabla = dynarray_create(sizeof(dnabla_t *), 128);
	dynarr_dnabla_rdx = dynarray_create(sizeof(dnabla_t *), 128);

	ctx.dynarr_dnabla = dynarr_dnabla;
	ctx.dynarr_dnabla_rdx = dynarr_dnabla_rdx;

	init_tickcount();
	if ((count = lib_iterlst(path_list, func_extract_list, &ctx)) < 0) {
		dynarray_free(dynarr_dnabla);
		dynarray_free(dynarr_dnabla_rdx);
		return -1;
	}
	printf("extraction time: %.3f (sec)\n", (float)(get_tickcount() / 1000.0));

	*pdynarr_dnabla = dynarr_dnabla;
	*pdynarr_dnabla_rdx = dynarr_dnabla_rdx;

	return count;
}

static bool
mkdb_imgpath(const char *imgpath)
{
	dnabla_t	*dnabla, *dnabla_rdx;
	bool	res;

	if (!extract_imgpath(imgpath, &dnabla, &dnabla_rdx))
		return false;

	res = ndb_insert(ndb, dnabla_rdx->pixels, dnabla->pixels);

	free_dnabla(dnabla_rdx);
	free_dnabla(dnabla);

	return res;
}

static bool
func_mkdb_img(const char *imgpath, void *ctx)
{
	return mkdb_imgpath(imgpath);
}

static bool
mkdb_img(const char *imgname)
{
	return try_iter_imgfmts(img_folder, imgname, func_mkdb_img, NULL);
}

static bool
func_mkdb_folder(const char *fname, const char *imgpath, void *ctx)
{
	return mkdb_imgpath(imgpath);
}

static bool
mkdb_folder(const char *path_folder)
{
	return iter_folder(path_folder, func_mkdb_folder, NULL);
}

static void
free_dynarr_dnablas(void *dynarr_dnabla1, void *dynarr_dnabla2)
{
	int	count = dynarray_count(dynarr_dnabla1);

	for (int i = 0; i < count; i++) {
		dnabla_t	*dnabla;

		dnabla = *(dnabla_t **)dynarray_get(dynarr_dnabla1, i + 1);
		free_dnabla(dnabla);
		dnabla = *(dnabla_t **)dynarray_get(dynarr_dnabla2, i + 1);
		free_dnabla(dnabla);
	}
	dynarray_free(dynarr_dnabla1);
	dynarray_free(dynarr_dnabla2);
}

static bool
mkdb_list(const char *path_list)
{
	void	*dynarr_dnabla, *dynarr_dnabla_rdx;
	bool	res = true;
	int	count;

	count = extract_img_list(path_list, &dynarr_dnabla, &dynarr_dnabla_rdx);
	if (count < 0)
		return false;

	init_tickcount();
	for (int i = 0; i < count; i++) {
		dnabla_t	*dnabla, *dnabla_rdx;

		dnabla = *(dnabla_t **)dynarray_get(dynarr_dnabla, i + 1);
		dnabla_rdx = *(dnabla_t **)dynarray_get(dynarr_dnabla_rdx, i + 1);
		res = ndb_insert(ndb, dnabla_rdx->pixels, dnabla->pixels);
		if (!res)
			break;
	}
	printf("insert time: %.3f (sec)\n", (float)(get_tickcount() / 1000.0));

	free_dynarr_dnablas(dynarr_dnabla, dynarr_dnabla_rdx);

	return res;
}

static int
search_imgpath(const char *imgpath, double *psimilarity)
{
	dnabla_t	*dnabla, *dnabla_rdx;
	ibmp_t	*ibmp;
	int	searched;

	ibmp = ibmp_load(imgpath);
	if (ibmp == NULL) {
		errmsg("failed to load: %s", imgpath);
		return -1;
	}

	dnabla_rdx = build_nabla_dna(ibmp, resol_rdx, depth_rdx);
	dnabla = build_nabla_dna(ibmp, resol_dna, depth_dna);
	ibmp_free(ibmp);

	searched = ndb_search(ndb, dnabla_rdx->pixels, dnabla->pixels, psimilarity);
	if (*psimilarity < threshold)
		searched = -1;

	free_dnabla(dnabla_rdx);
	free_dnabla(dnabla);

	return searched;
}

typedef struct {
	unsigned int	id_searched;
	double	similarity;
} search_img_ctx_t;

static bool
func_search_img(const char *imgpath, void *ctx)
{
	search_img_ctx_t	*pctx = (search_img_ctx_t *)ctx;

	pctx->id_searched = search_imgpath(imgpath, &pctx->similarity);
	return true;
}

static int
search_img(const char *imgname, double *psimilarity)
{
	search_img_ctx_t	ctx;

	if (!try_iter_imgfmts(img_folder, imgname, func_search_img, (void *)&ctx)) {
		errmsg("not found image: %s", imgname);
		return -1;
	}
	*psimilarity = ctx.similarity;
	return ctx.id_searched;
}

#define FNAME_MAX	128

typedef struct {
	char	fname[FNAME_MAX];
	unsigned int	id_searched;
	double	similarity;
} search_info_folder_t;

static bool
func_search_folder(const char *fname, const char *imgpath, void *ctx)
{
	int	id_searched;
	double	similarity;

	id_searched = search_img(imgpath, &similarity);
	if (id_searched >= 0) {
		search_info_folder_t	*info = (search_info_folder_t *)dynarray_add(ctx);
		info->id_searched = (unsigned int)id_searched;
		info->similarity = similarity;
		strncpy(info->fname, fname, FNAME_MAX);
	}
	return true;
}

static void
search_folder(const char *path_folder)
{
	void	*search_infos = dynarray_create(sizeof(search_info_folder_t), 16);
	unsigned int	count;

	iter_folder(path_folder, func_search_folder, search_infos);

	count = dynarray_count(search_infos);
	for (int i = 0; i < count; i++) {
		search_info_folder_t	*info = dynarray_get(search_infos, i + 1);
		printf("%s: %d\n", info->fname, info->id_searched);
	}
	dynarray_free(search_infos);
}

typedef struct {
	unsigned int	idx;
	unsigned int	id_searched;
	double		similarity;
} search_info_list_t;

static void
search_list(const char *path_list)
{
	void	*dynarr_dnabla, *dynarr_dnabla_rdx;
	void	*search_infos = dynarray_create(sizeof(search_info_list_t), 16);
	int	count, n_searched;

	count = extract_img_list(path_list, &dynarr_dnabla, &dynarr_dnabla_rdx);
	if (count < 0)
		return;

	init_tickcount();
	for (int i = 0; i < count; i++) {
		dnabla_t	*dnabla, *dnabla_rdx;
		double		similarity;
		int	id_searched;

		dnabla = *(dnabla_t **)dynarray_get(dynarr_dnabla, i + 1);
		dnabla_rdx = *(dnabla_t **)dynarray_get(dynarr_dnabla_rdx, i + 1);
		id_searched = ndb_search(ndb, dnabla_rdx->pixels, dnabla->pixels, &similarity);
		if (similarity >= threshold) {
			search_info_list_t	*info = dynarray_add(search_infos);
			info->idx = i + 1;
			info->id_searched = (unsigned int)id_searched;
			info->similarity = similarity;
		}
	}
	printf("search time: %.3f (sec)\n", (float)(get_tickcount() / 1000.0));

	n_searched = dynarray_count(search_infos);
	printf("matched ratio: %.2f (%%)\n", (float)(n_searched * 100.0 / count));

	for (int i = 0; i < n_searched; i++) {
		search_info_list_t	*info = dynarray_get(search_infos, i + 1);
		printf("%d: %d, %.4lf\n", info->idx, info->id_searched, info->similarity);
	}
	dynarray_free(search_infos);

	free_dynarr_dnablas(dynarr_dnabla, dynarr_dnabla_rdx);
}

int
main(int argc, char *argv[])
{
	bool	res;

	setup_env();
	parse_args(argc, argv);

	if (insert_mode) {
		if (is_folder(inpath))
			res = mkdb_folder(inpath);
		else {
			if (path_has_ext(inpath, "txt"))
				res = mkdb_list(inpath);
			else
				res = mkdb_img(inpath);
		}
		if (res) {
			ndb_store(ndb, path_ndb);
			printf("db stored: %s\n", path_ndb);
		}
		else {
			errmsg("mkdb failed");
		}
	}
	else {
		if (is_folder(inpath))
			search_folder(inpath);
		else {
			if (path_has_ext(inpath, "txt"))
				search_list(inpath);
			else {
				int	id_searched;
				double	similarity;

				id_searched = search_img(inpath, &similarity);
				if (id_searched >= 0)
					printf("searched: %d, %.4lf\n", id_searched, similarity);
			}
		}
	}

	ndb_close(ndb);

	return 0;
}
