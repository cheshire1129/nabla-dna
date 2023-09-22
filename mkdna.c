#include "config.h"

#include <stdio.h>

#include "ibmp.h"

int
main(int argc, char *argv[])
{
	ibmp_t	*pbmp;

	pbmp = ibmp_load(argv[1]);
	if (pbmp == NULL) {
		printf("failed to load]n");
		return 1;
	}
	printf("width x height: %d x %d\n", pbmp->width, pbmp->height);

	{
		int	i;

		for (i = 0; i < pbmp->width * pbmp->height; i++) {
			printf("%.2f ", pbmp->pixels[i]);///TEST
		}
	}
	
	return 0;
}
