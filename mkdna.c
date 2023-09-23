#include "config.h"

#include <stdio.h>

#include "ibmp.h"
#include "nabla_dna.h"

int
main(int argc, char *argv[])
{
	dnabla_t	*dnabla;
	ibmp_t	*pbmp;
	
	pbmp = ibmp_load(argv[1]);
	if (pbmp == NULL) {
		printf("failed to load]n");
		return 1;
	}
	printf("width x height: %d x %d\n", pbmp->width, pbmp->height);

	{
		int	i, j;
		float	*p;

		p = pbmp->pixels;
		for (i = 0; i < pbmp->height; i++) {
			for (j = 0; j < pbmp->width; j++, p++) {
				printf("%3.2f ", *p);
			}
			printf("\n");
		}
	}

	dnabla = build_nabla_dna(pbmp, 3);

	{
		int	i, j;
		int	*p, n_pixels;

		p = dnabla->pixels;
		n_pixels = get_n_nabla_pixels(dnabla->size);
		for (i = 0; i < n_pixels; i++, p++) {
			printf("%3u ", *p);
		}
		printf("\n");
	}

	return 0;
}
