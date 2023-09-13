#include <stdio.h>
#include <stdlib.h>

#include "graybmp.h"

static bool
is_big_endian(void)
{
	uint16_t	value = 0x0001;

	return (*(uint8_t *)&value) != 0x01;
}

#define UINT16_SWAP_LE_BE_CONSTANT(val)		\
  ((uint16_t)					\
   (						\
    (uint16_t) ((uint16_t) (val) >> 8) |	\
    (uint16_t) ((uint16_t) (val) << 8)))

#define UINT32_SWAP_LE_BE_CONSTANT(val)			  \
  ((uint32_t)						  \
   (							  \
    (((uint32_t) (val) & (uint32_t) 0x000000ffU) << 24) | \
    (((uint32_t) (val) & (uint32_t) 0x0000ff00U) <<  8) | \
    (((uint32_t) (val) & (uint32_t) 0x00ff0000U) >>  8) | \
    (((uint32_t) (val) & (uint32_t) 0xff000000U) >> 24)))

static void
bmp_header_swap_endianess(bmp_header_t *phdr)
{
	phdr->filesz = UINT32_SWAP_LE_BE_CONSTANT(phdr->filesz);
	phdr->creator1 = UINT16_SWAP_LE_BE_CONSTANT(phdr->creator1);
	phdr->creator2 = UINT16_SWAP_LE_BE_CONSTANT(phdr->creator2);
	phdr->offset = UINT32_SWAP_LE_BE_CONSTANT(phdr->offset);
}

static void
bmp_dib_v3_header_swap_endianess(bmp_dib_v3_header_t *pdib)
{
	pdib->header_sz = UINT32_SWAP_LE_BE_CONSTANT(pdib->header_sz);
	pdib->width = UINT32_SWAP_LE_BE_CONSTANT(pdib->width);
	pdib->height = UINT32_SWAP_LE_BE_CONSTANT(pdib->height);
	pdib->nplanes = UINT16_SWAP_LE_BE_CONSTANT(pdib->nplanes);
	pdib->depth = UINT16_SWAP_LE_BE_CONSTANT(pdib->depth);
	pdib->compress_type = UINT32_SWAP_LE_BE_CONSTANT(pdib->compress_type);
	pdib->bmp_bytesz = UINT32_SWAP_LE_BE_CONSTANT(pdib->bmp_bytesz);
	pdib->hres = UINT32_SWAP_LE_BE_CONSTANT(pdib->hres);
	pdib->vres = UINT32_SWAP_LE_BE_CONSTANT(pdib->vres);
	pdib->ncolors = UINT32_SWAP_LE_BE_CONSTANT(pdib->ncolors);
	pdib->nimpcolors = UINT32_SWAP_LE_BE_CONSTANT(pdib->nimpcolors);
}

static bool
bmp_read_header(graybmp_t *pbmp, FILE *fp)
{
	bmp_header_t	*phdr = &pbmp->header;

	if (fread(phdr, sizeof(bmp_header_t), 1, fp) != 1)
		return FALSE;

	if (is_big_endian())
		bmp_header_swap_endianess(phdr);

	if (phdr->magic[0] != 'B' || phdr->magic[1] != 'M')
		return FALSE;
	return TRUE;
}

#define BMP_WIDTH_BYTESZ(width)	((((width) * 3 + 3) / 4) * 4)

static bool
bmp_read_dib(graybmp_t *pbmp, FILE *fp)
{
	bmp_dib_v3_header_t	*pdib = &pbmp->dib;

	if (fread(pdib, sizeof(bmp_dib_v3_header_t), 1, fp) != 1)
		return FALSE;

	if (is_big_endian())
		bmp_dib_v3_header_swap_endianess(pdib);

	/* sanity check */
	if (pdib->header_sz != 40)
		return FALSE;
	if (pdib->depth != 24)
		return FALSE;
	if (pdib->compress_type != 0)
		return FALSE;
	if (pdib->nplanes != 1)
		return FALSE;
	if (pdib->bmp_bytesz != BMP_WIDTH_BYTESZ(pdib->width) * pdib->height)
		return FALSE;
	return TRUE;
}

#define ROWMAX	300
#define TO_GRAYED_INTENSITY(r, g, b)	((r) * 0.299 + (g) * 0.587 + (b) * 0.114)

static bool
load_grayed_pixels_line(float *grayed_pixels, int width, FILE *fp)
{
	int	remain = width;

	while (remain > 0) {
		uint8_t	buf[ROWMAX * 3], *bref;
		int	width_sub, nread;
		int	w;

		if (remain < ROWMAX) {
			width_sub = remain;
			nread = BMP_WIDTH_BYTESZ(remain);
		}
		else {
			width_sub = ROWMAX;
			nread = ROWMAX * 3;
		}
		if (fread(buf, nread, 1, fp) != 1)
			return FALSE;

		bref = buf;
		for (w = 0; w < width_sub; w++, bref += 3) {
			grayed_pixels[w] = TO_GRAYED_INTENSITY(bref[0], bref[1], bref[2]);
		}

		remain -= nread;
	}
	return TRUE;
}

static bool
bmp_load_grayed_pixels(graybmp_t *pbmp, FILE *fp)
{
	bmp_dib_v3_header_t	*pdib = &pbmp->dib;
	float	*pixels;
	int	h;

	pbmp->grayed_pixels = pixels = (float *)malloc(pdib->width * pdib->height * sizeof(float));
	if (pbmp->grayed_pixels == NULL)
		return FALSE;
	pixels += (pdib->height - 1) * pdib->width;
	for (h = 0; h < pdib->height; h++) {
		if (!load_grayed_pixels_line(pixels, pdib->width, fp))
			return FALSE;
		pixels -= pdib->width;
	}
	return TRUE;
}

bool
graybmp_load(graybmp_t *pbmp, const char *fname)
{
	FILE	*fp;
	int	row;
	unsigned char *buf;

	if ((fp = fopen(fname, "rb")) == NULL)
		return FALSE;

	/* read the file */
	if (!bmp_read_header(pbmp, fp) ||
	    !bmp_read_dib(pbmp, fp) ||
	    !bmp_load_grayed_pixels(pbmp, fp)) {
		fclose(fp);
		return FALSE;
	}

	fclose(fp);

	return TRUE;
}
