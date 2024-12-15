#include "config.h"

#include <stdlib.h>
#include <math.h>

#include "xbmp.h"
#include "nabla_dna.h"

static uint8_t *
get_quantized_bmp(xbmp_t *nbmp, int dna_depth)
{
	uint8_t	*pixels;
	int	pixel_max;
	float	depth_adj;
	int	n_pixels;
	int	i;

	n_pixels = get_n_nabla_pixels(nbmp->size);
	pixels = (uint8_t *)malloc(n_pixels * sizeof(uint8_t));
	if (pixels == NULL)
		return NULL;

	pixel_max = 2 << (dna_depth - 1);
	depth_adj = (pixel_max - 1) / 255.0;
	for (i = 0; i < n_pixels; i++) {
		pixels[i] = (uint8_t)floor(nbmp->pixels[i] * depth_adj);
		if (pixels[i] >= pixel_max)
			pixels[i]--;
	}

	return pixels;
}

dnabla_t *
build_nabla_dna(ibmp_t *ibmp, int dna_resol, int dna_depth)
{
	xbmp_t	*nbmp;
	dnabla_t	*dnabla;

	nbmp = build_nabla_bmp(ibmp, dna_resol);
	if (nbmp == NULL)
		return NULL;

	dnabla = (dnabla_t *)malloc(sizeof(dnabla_t));
	if (dnabla == NULL) {
		free_xbmp(nbmp);
		return NULL;
	}
	dnabla->dna_size = nbmp->size;
	dnabla->pixels = get_quantized_bmp(nbmp, dna_depth);

	free_xbmp(nbmp);

	return dnabla;
}

void
free_dnabla(dnabla_t *dnabla)
{
	if (dnabla == NULL)
		return;
	if (dnabla->pixels)
		free(dnabla->pixels);
	free(dnabla);
}
