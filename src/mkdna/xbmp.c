#include "config.h"

#include <stdio.h>
#include <math.h>
#include <stdlib.h>

#include "ibmp.h"
#include "xbmp.h"

static float
get_intensity_sum(ibmp_t *pbmp, float fws, float fwe, float fhs, float fhe)
{
	float	*pixel_rowhead;
	float	intensity_sum = 0;
	int	ws, we, hs, he;
	int	w, h;

	ws = (int)floorf(fws);
	we = (int)ceilf(fwe);
	hs = (int)floorf(fhs);
	he = (int)ceilf(fhe);

	pixel_rowhead = pbmp->pixels + hs * pbmp->width;
	for (h = hs; h < he; h++, pixel_rowhead += pbmp->width) {
		float	*pixel = pixel_rowhead;
		float	weight = 1;

		if (h == hs)
			weight *= (1 - (fhs - hs));
		else if (h == he - 1)
			weight *= (fhe - (he - 1));

		pixel += ws;
		for (w = ws; w < we; w++, pixel++) {
			float	weight_cur = weight;

			if (w == ws)
				weight_cur = weight * (1 - (fws - ws));
			else if (w == we - 1)
				weight_cur = weight * (fwe - (we - 1));
			
			intensity_sum += (*pixel * weight_cur);
		}
	}

	return intensity_sum;
}

static xbmp_t *
build_avg_bmp(ibmp_t *ibmp, int size)
{
	xbmp_t	*abmp;
	float	unit_w, unit_h, unit_pixels;
	float	*pixel_avg;
	int	w, h;

	abmp = malloc(sizeof(xbmp_t));
	if (abmp == NULL)
		return NULL;
	abmp->size = size;
	abmp->pixels = pixel_avg = (float *)malloc(size * size * sizeof(float));
	if (pixel_avg == NULL) {
		free(abmp);
		return false;
	}

	unit_w = (float)ibmp->width / size;
	unit_h = (float)ibmp->height / size;
	unit_pixels = unit_w * unit_h;

	for (h = 0; h < size; h++) {
		for (w = 0; w < size; w++, pixel_avg++) {
			float	intensity_sum;

			intensity_sum = get_intensity_sum(ibmp, unit_w * w, unit_w * (w + 1), unit_h * h, unit_h * (h + 1));
			*pixel_avg = intensity_sum / unit_pixels;
		}
	}

	return abmp;
}

int
get_n_nabla_pixels(int dna_size)
{
	if (dna_size % 2) {
		return (dna_size + 1) * (dna_size - 1) / 2 / 2 + 1;
	}
	else {
		return dna_size * ((dna_size - 1) / 2 + 1) / 2;
	}
}

static bool
rotate_avg_bmp(xbmp_t *abmp)
{
	int	size = abmp->size;
	int	n_nabla_pixels;
	float	*pixels, *pixel;
	int	w, h;

	pixel = pixels = malloc(get_n_nabla_pixels(size) * sizeof(float));
	for (h = 0; h < (size + 1) / 2; h++) {
		for (w = h; w < size - h - 1 || (w == h && w == (size + 1) / 2 - 1 && size % 2); w++) {
			float	merged;

			merged = abmp->pixels[h * size + w];
			merged += abmp->pixels[(size - 1 - w) * size + h];		// 90 degree
			merged += abmp->pixels[(size - 1 - h) * size + size - 1 - w];	// 180 degree
			merged += abmp->pixels[w * size + size - 1 - h];		// 90 degree
			merged /= 4;
			*pixel++ = merged;
		}
	}
	free(abmp->pixels);
	abmp->pixels = pixels;
	return true;
}

static bool
normalize_bmp(xbmp_t *rbmp)
{
	float	*pixels;
	float	vmin, vmax;
	int	n_pixels = get_n_nabla_pixels(rbmp->size);
	int	i;

	pixels = (float *)malloc(n_pixels * sizeof(int));
	if (pixels == NULL)
		return NULL;

	vmax = vmin = rbmp->pixels[0];
	for (i = 1; i < n_pixels; i++) {
		if (rbmp->pixels[i] < vmin)
			vmin = pixels[i];
		else if (rbmp->pixels[i] > vmax)
			vmax = pixels[i];
	}
	if (vmin == vmax) {
		for (i = 0; i < n_pixels; i++)
			pixels[i] = 0;
	}
	else {
		for (i = 0; i < n_pixels; i++)
			pixels[i] = (rbmp->pixels[i] - vmin) * 255 / (vmax - vmin);
	}

	free(rbmp->pixels);
	rbmp->pixels = pixels;

	return true;
}

void
free_xbmp(xbmp_t *xbmp)
{
	if (xbmp == NULL)
		return;
	if (xbmp->pixels)
		free(xbmp->pixels);
	free(xbmp);
}

xbmp_t *
build_nabla_bmp(ibmp_t *ibmp, int dna_size)
{
	xbmp_t	*xbmp;

	xbmp = build_avg_bmp(ibmp, dna_size);
	if (xbmp == NULL)
		return NULL;
	if (!rotate_avg_bmp(xbmp)) {
		free_xbmp(xbmp);
		return NULL;
	}

	if (!normalize_bmp(xbmp)) {
		free_xbmp(xbmp);
		return NULL;
	}
	return xbmp;
}
