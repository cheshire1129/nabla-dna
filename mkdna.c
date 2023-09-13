#include "config.h"

#include <stdio.h>

#include "graybmp.h"

int
main(int argc, char *argv[])
{
	graybmp_t	bmp;

	printf("loaded: %d\n", graybmp_load(&bmp, argv[1]));
	printf("width x height: %d x %d\n", bmp.dib.width, bmp.dib.height);
	printf("bmp_bytesz: %d\n", bmp.dib.bmp_bytesz);

	{
		int	i;

		for (i = 0; i < bmp.dib.width * bmp.dib.height; i++) {
			printf("%.2f ", bmp.grayed_pixels[i]);///TEST
		}
	}
	
	return 0;
}
