#include "config.h"

#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <stdbool.h>

#include "util.h"
#include "ibmp.h"
#include "nabla_dna.h"
#include "similarity.h"

static int	resol = 8;
static int	depth = 8;
static const char	*inpath1, *inpath2;
static const char	*img_folder;

static void
usage(void)
{
	printf(
"Usage: getdist [<options>] <image name> <image name>\n"
"   <options>\n"
"   -h: help(this message)\n"
"   -I <image folder>: image folder(env var: IMAGE_FOLDER)\n"
"   -x <dna resolution>: dna resolutions of image (default: 8)\n"
"   -d <dna depth>: dna depth (default: 8)\n"
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

        while ((c = getopt(argc, argv, "hI:x:d:")) != -1) {
                switch (c) {
		case 'I':
			img_folder = optarg;
			break;
                case 'x':
                        if (sscanf(optarg, "%d", &resol) != 1) {
                                usage();
                                exit(1);
                        }
                        break;
                case 'd':
                        if (sscanf(optarg, "%d", &depth) != 1) {
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
	if (argc - optind < 2) {
		usage();
		exit(1);
	}
	inpath1 = argv[optind];
	inpath2 = argv[optind + 1];
}

static bool
func_load_dnabla(const char *imgpath, void *ctx)
{
	dnabla_t	**pnabla = (dnabla_t **)ctx;
	ibmp_t	*ibmp;

	ibmp = ibmp_load(imgpath);
	if (ibmp == NULL)
		return false;

	*pnabla = build_nabla_dna(ibmp, resol, depth);
	ibmp_free(ibmp);

	return true;
}

static dnabla_t *
load_dnabla(const char *path)
{
	dnabla_t	*dnabla;

	if (!try_iter_imgfmts(img_folder, path, func_load_dnabla, &dnabla)) {
		errmsg("failed to load: %s", path);
		return NULL;
	}

	return dnabla;
}

static bool
getdist(void)
{
	dnabla_t	*dnabla1, *dnabla2;
	double	similarity;
	int	size;

	if ((dnabla1 = load_dnabla(inpath1)) == NULL)
		return false;
	if ((dnabla2 = load_dnabla(inpath2)) == NULL) {
		free_dnabla(dnabla2);
		return false;
	}

	size = get_n_nabla_pixels(resol);
	similarity = get_similarity(dnabla1->pixels, dnabla2->pixels, size);
	printf("similarity: %lf\n", similarity);

	return true;
}

int
main(int argc, char *argv[])
{
	setup_env();
	parse_args(argc, argv);

	if (!getdist())
		return 2;
	return 0;
}
