#include "config.h"

#include <stdlib.h>
#include <math.h>

#include "xbmp.h"
#include "nabla_dna.h"

static uint8_t *
get_quantized_bmp(xbmp_t *nbmp)
{
	uint8_t	*pixels;
	int	n_pixels;
	int	i;

	n_pixels = get_n_nabla_pixels(nbmp->size);
	pixels = (uint8_t *)malloc(n_pixels * sizeof(uint8_t));
	if (pixels == NULL)
		return NULL;
	for (i = 0; i < n_pixels; i++)
		pixels[i] = (uint8_t)round(nbmp->pixels[i]);

	return pixels;
}

dnabla_t *
build_nabla_dna(ibmp_t *ibmp, int dna_size)
{
	xbmp_t	*nbmp;
	dnabla_t	*dnabla;

	nbmp = build_nabla_bmp(ibmp, dna_size);
	if (nbmp == NULL)
		return NULL;

	dnabla = (dnabla_t *)malloc(sizeof(dnabla_t));
	if (dnabla == NULL) {
		free_xbmp(nbmp);
		return NULL;
	}
	dnabla->size = nbmp->size;
	dnabla->pixels = get_quantized_bmp(nbmp);

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
