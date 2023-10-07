#include "config.h"

#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <stdarg.h>

#include "ibmp.h"
#include "nabla_dna.h"

static int	size = 4;
static const char	*imgpath;
static const char	*outpath;

static void
usage(void)
{
	printf(
"Usage: mkdna [<options>] <image path>\n"
"   <options>\n"
"   -h: help(this message)\n"
"   -s <size>: dna size (default: 4)\n"
"   -o <output>: save dna as text\n"
		);
}

void
errmsg(const char *fmt, ...)
{
        va_list ap;
        char    *errmsg;

        va_start(ap, fmt);
        vasprintf(&errmsg, fmt, ap);
        va_end(ap);

        fprintf(stderr, "ERROR: %s\n", errmsg);

        free(errmsg);
}

static void
parse_args(int argc, char *argv[])
{
        int     c;

        while ((c = getopt(argc, argv, "hs:o:")) != -1) {
                switch (c) {
                case 's':
                        if (sscanf(optarg, "%d", &size) != 1) {
                                usage();
                                exit(1);
                        }
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
	imgpath = argv[optind];
}

static void
save_dnabla(FILE *fp, dnabla_t *dnabla)
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

int
main(int argc, char *argv[])
{
	dnabla_t	*dnabla;
	ibmp_t	*ibmp;

	parse_args(argc, argv);

	ibmp = ibmp_load(imgpath);
	if (ibmp == NULL) {
		errmsg("failed to load: %s", imgpath);
		return 1;
	}

	dnabla = build_nabla_dna(ibmp, size);
	ibmp_free(ibmp);

	if (outpath != NULL) {
		FILE	*outf;

		outf = fopen(outpath, "w");
		if (outf == NULL) {
			errmsg("failed to write: %s", outpath);
			return 2;
		}
		save_dnabla(outf, dnabla);
		fclose(outf);
	}
	else {
		save_dnabla(stdout, dnabla);
	}

	free_dnabla(dnabla);

	return 0;
}
