#include "config.h"

#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <stdbool.h>

#include "ibmp.h"
#include "nabla_dna.h"
#include "util.h"

static int	size = 4;
static const char	*inpath;
static const char	*outpath;
static const char	*img_folder;

static void
usage(void)
{
	printf(
"Usage: mkdna [<options>] <image name/path/folder or list file>\n"
"   A list file must have a .txt extension\n"
"   <options>\n"
"   -h: help(this message)\n"
"   -s <size>: dna size (default: 4)\n"
"   -I <image folder>: image folder(env var: IMAGE_FOLDER)\n"
"   -o <output>: save dna as text\n"
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

        while ((c = getopt(argc, argv, "hs:Io:")) != -1) {
                switch (c) {
                case 's':
                        if (sscanf(optarg, "%d", &size) != 1) {
                                usage();
                                exit(1);
                        }
                        break;
		case 'I':
			img_folder = optarg;
			break;
		case 'o':
			outpath = optarg;
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
	inpath = argv[optind];
}

static void
write_dnabla(FILE *fp, dnabla_t *dnabla)
{
	int	i;
	uint8_t	*p;
	int	n_pixels;

	p = dnabla->pixels;
	n_pixels = get_n_nabla_pixels(dnabla->size);
	for (i = 0; i < n_pixels; i++, p++) {
		fprintf(fp, "%3hhu ", *p);
	}
	fprintf(fp, "\n");
}

static bool
save_dnabla(const char *path, dnabla_t *dnabla)
{
	FILE	*outf;

	outf = fopen(path, "w");
	if (outf == NULL) {
		errmsg("failed to write: %s", path);
		return false;
	}
	write_dnabla(outf, dnabla);
	fclose(outf);

	return true;
}

static bool
mkdna_imgpath(const char *fname, const char *imgpath)
{
	dnabla_t	*dnabla;
	ibmp_t	*ibmp;
	bool	res = true;

	ibmp = ibmp_load(imgpath);
	if (ibmp == NULL) {
		errmsg("failed to load: %s", imgpath);
		return false;
	}

	dnabla = build_nabla_dna(ibmp, size);
	ibmp_free(ibmp);

	if (outpath != NULL) {
		if (fname) {
			char	*path_new, *fname_new;

			fname_new = path_get_replaced_ext(fname, "pis");
			path_new = path_join(outpath, fname_new);
			free(fname_new);
			res = save_dnabla(path_new, dnabla);
			free(path_new);
		}
		else
			res = save_dnabla(outpath, dnabla);
	}
	else {
		if (fname)
			printf("%s: ", fname);
		write_dnabla(stdout, dnabla);
	}

	free_dnabla(dnabla);

	return res;
}

static bool
func_mkdna_img(const char *imgpath, void *ctx)
{
	const char	*fname = (const char *)ctx;

	return mkdna_imgpath(fname, imgpath);
}

static bool
mkdna_img(const char *fname, const char *imgname)
{
	return try_iter_imgfmts(img_folder, imgname, func_mkdna_img, (void *)fname);
}

static bool
func_mkdna_folder(const char *fname, const char *imgpath, void *ctx)
{
	return mkdna_imgpath(path_basename(imgpath), imgpath);
}

static bool
mkdna_folder(const char *path_folder)
{
	return iter_folder(path_folder, func_mkdna_folder, NULL);
}

static bool
func_mkdna_list(unsigned int idx, const char *img_name, void *ctx)
{
	return mkdna_img(img_name, img_name);
}

static bool
mkdna_list(const char *path_list)
{
	return lib_iterlst(path_list, func_mkdna_list, NULL);
}

int
main(int argc, char *argv[])
{
	bool	res;

	setup_env();
	parse_args(argc, argv);

	if (is_folder(inpath))
		res = mkdna_folder(inpath);
	else {
		if (path_has_ext(inpath, "txt"))
			res = mkdna_list(inpath);
		else
			res = mkdna_img(NULL, inpath);
	}

	return (res) ? 0: 2;
}
