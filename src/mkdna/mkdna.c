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
mkdna_img(const char *fname, const char *imgname)
{
	const char	*ext_names[] = { "jpg", "png", "gif", "bmp", "jpeg", "JPG", "PNG", "GIF", "BMP", "JPEG" };
	int	i;

	if (path_exist(imgname))
		return mkdna_imgpath(fname, imgname);
	for (i = 0; i < sizeof(ext_names) / sizeof(const char *); i++) {
		char	*imgpath = path_build(img_folder, imgname, ext_names[i]);
		if (path_exist(imgpath)) {
			bool	res = mkdna_imgpath(fname, imgpath);
			free(imgpath);
			return res;
		}
		free(imgpath);
	}
	return false;
}

static bool
mkdna_folder(const char *path_folder)
{
	const char	*name;
	void	*dir;
	bool	res = true;

	dir = lib_opendir(path_folder);
	if (dir == NULL)
		return false;

	while (res && (name = lib_readdir(dir))) {
		char	*imgpath;

		imgpath = path_join(path_folder, name);
		res = mkdna_imgpath(name, imgpath);
		free(imgpath);
	}

	lib_closedir(dir);

	return res;
}

static bool
mkdna_list(const char *path_list)
{
	void	*lst;
	const char	*img_name;

	if ((lst = lib_openlst(path_list)) == NULL)
		return false;

	while ((img_name = lib_readlst(lst))) {
		if (!mkdna_img(img_name, img_name)) {
			lib_closelst(lst);
			return false;
		}
	}
	lib_closelst(lst);
	return true;
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
