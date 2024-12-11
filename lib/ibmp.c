#include "config.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#include "ibmp.h"

#define TO_GRAYED_INTENSITY(r, g, b)	((r) * 0.299 + (g) * 0.587 + (b) * 0.114)

static void
load_grayed_pixels_line(float *grayed_pixels, int width, int channels, unsigned char *bitmap_line)
{
	unsigned char	*pixel;
	int	x;

	for (x = 0, pixel = bitmap_line; x < width; x++, pixel += channels)
		grayed_pixels[x] = TO_GRAYED_INTENSITY(pixel[0], pixel[1], pixel[2]);
}

static bool
bmp_load_grayed_pixels(ibmp_t *pbmp, unsigned char *bitmap)
{
	float	*pixels;
	unsigned char	*bitmap_line;
	int	h;

	pbmp->pixels = pixels = (float *)malloc(pbmp->width * pbmp->height * sizeof(float));
	if (pbmp->pixels == NULL)
		return false;
	for (h = 0, bitmap_line = bitmap; h < pbmp->height; h++, bitmap_line += pbmp->width * pbmp->channels) {
		load_grayed_pixels_line(pixels, pbmp->width, pbmp->channels, bitmap_line);
		pixels += pbmp->width;
	}
	return true;
}

ibmp_t *
ibmp_load(const char *fname)
{
	ibmp_t		*pbmp;
	unsigned char	*bitmap;
	int	width, height, channels;

	bitmap = stbi_load(fname, &width, &height, &channels, 0);
	if (bitmap == NULL)
		return NULL;

	pbmp = (ibmp_t *)malloc(sizeof(ibmp_t));
	if (pbmp == NULL) {
		stbi_image_free(bitmap);
		return NULL;
	}

	pbmp->width = width;
	pbmp->height = height;
	pbmp->channels = channels;

	if (!bmp_load_grayed_pixels(pbmp, bitmap)) {
		stbi_image_free(bitmap);
		free(pbmp);
		return NULL;
	}
	stbi_image_free(bitmap);

	return pbmp;
}

void
ibmp_free(ibmp_t *pbmp)
{
	if (pbmp == NULL)
		return;
	if (pbmp->pixels)
		free(pbmp->pixels);
	free(pbmp);
}
