#include "config.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "ibmp.h"

typedef struct __attribute__((packed)) {
	uint8_t		magic[2];	/* the magic number used to identify the BMP file:
					   0x42 0x4D (Hex code points for B and M).
					   The following entries are possible:
					   BM - Windows 3.1x, 95, NT, ... etc
					   BA - OS/2 Bitmap Array
					   CI - OS/2 Color Icon
					   CP - OS/2 Color Pointer
					   IC - OS/2 Icon
					   PT - OS/2 Pointer. */
	uint32_t	filesz;		/* the size of the BMP file in bytes */
	uint16_t	creator1;	/* reserved. */
	uint16_t	creator2;	/* reserved. */
	uint32_t	offset;		/* the offset, i.e. starting address,
					   of the byte where the bitmap data can be found. */
} bmp_hdr_t;

typedef struct {
	uint32_t	header_sz;	/* the size of this header (40 bytes) */
	uint32_t	width;         /* the bitmap width in pixels */
	uint32_t	height;        /* the bitmap height in pixels */
	uint16_t	nplanes;       /* the number of color planes being used.
					  Must be set to 1. */
	uint16_t	depth;         /* the number of bits per pixel,
					  which is the color depth of the image.
					  Typical values are 1, 4, 8, 16, 24 and 32. */
	uint32_t	compress_type; /* the compression method being used.
					  See also bmp_compression_method_t. */
	uint32_t	bmp_bytesz;    /* the image size. This is the size of the raw bitmap
					  data (see below), and should not be confused
					  with the file size. */
	uint32_t	hres;          /* the horizontal resolution of the image.
					  (pixel per meter) */
	uint32_t	vres;          /* the vertical resolution of the image.
					  (pixel per meter) */
	uint32_t	ncolors;       /* the number of colors in the color palette,
					  or 0 to default to 2<sup><i>n</i></sup>. */
	uint32_t	nimpcolors;    /* the number of important colors used,
					  or 0 when every color is important;
					  generally ignored. */
} bmp_hdr_dibv3_t;

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
bmp_header_swap_endianess(bmp_hdr_t *phdr)
{
	phdr->filesz = UINT32_SWAP_LE_BE_CONSTANT(phdr->filesz);
	phdr->creator1 = UINT16_SWAP_LE_BE_CONSTANT(phdr->creator1);
	phdr->creator2 = UINT16_SWAP_LE_BE_CONSTANT(phdr->creator2);
	phdr->offset = UINT32_SWAP_LE_BE_CONSTANT(phdr->offset);
}

static void
bmp_dib_v3_header_swap_endianess(bmp_hdr_dibv3_t *pdib)
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

static int
bmp_read_header(bmp_hdr_t *phdr_bmp, FILE *fp)
{
	if (fread(phdr_bmp, sizeof(bmp_hdr_t), 1, fp) != 1)
		return -1;

	if (is_big_endian())
		bmp_header_swap_endianess(phdr_bmp);

	if (phdr_bmp->magic[0] != 'B' || phdr_bmp->magic[1] != 'M')
		return -1;
	return true;
}

#define BMP_WIDTH_BYTESZ(width)	((((width) * 3 + 3) / 4) * 4)

static bool
bmp_read_dib(bmp_hdr_dibv3_t *phdr_dibv3, bmp_hdr_t *phdr_bmp, FILE *fp)
{
	if (fread(phdr_dibv3, sizeof(bmp_hdr_dibv3_t), 1, fp) != 1)
		return false;

	if (is_big_endian())
		bmp_dib_v3_header_swap_endianess(phdr_dibv3);

	/* sanity check */
	if (phdr_dibv3->header_sz != 40)
		return false;
	if (phdr_dibv3->depth != 24)
		return false;
	if (phdr_dibv3->compress_type != 0)
		return false;
	if (phdr_dibv3->nplanes != 1)
		return false;
	if (phdr_dibv3->bmp_bytesz != BMP_WIDTH_BYTESZ(phdr_dibv3->width) * phdr_dibv3->height)
		return false;
	return true;
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
			return false;

		bref = buf;
		for (w = 0; w < width_sub; w++, bref += 3) {
			grayed_pixels[w] = TO_GRAYED_INTENSITY(bref[0], bref[1], bref[2]);
		}

		remain -= nread;
	}
	return true;
}

static bool
bmp_load_grayed_pixels(ibmp_t *pbmp, bmp_hdr_dibv3_t *phdr_dibv3, FILE *fp)
{
	float	*pixels;
	int	h;

	pbmp->pixels = pixels = (float *)malloc(phdr_dibv3->width * phdr_dibv3->height * sizeof(float));
	if (pbmp->pixels == NULL)
		return false;
	pixels += (phdr_dibv3->height - 1) * phdr_dibv3->width;
	for (h = 0; h < phdr_dibv3->height; h++) {
		if (!load_grayed_pixels_line(pixels, phdr_dibv3->width, fp))
			return false;
		pixels -= phdr_dibv3->width;
	}
	return true;
}

ibmp_t *
ibmp_load(const char *fname)
{
	ibmp_t		*pbmp;
	bmp_hdr_t	hdr_bmp;
	bmp_hdr_dibv3_t	hdr_dibv3;
	FILE	*fp;
	unsigned char *buf;

	if ((fp = fopen(fname, "rb")) == NULL)
		return NULL;

	/* read the file */
	if (!bmp_read_header(&hdr_bmp, fp) || !bmp_read_dib(&hdr_dibv3, &hdr_bmp, fp)) {
		fclose(fp);
		return false;
	}

	pbmp = (ibmp_t *)malloc(sizeof(ibmp_t));
	if (pbmp == NULL) {
		fclose(fp);
		return false;
	}
	if (!bmp_load_grayed_pixels(pbmp, &hdr_dibv3, fp)) {
		fclose(fp);
		free(pbmp);
		return false;
	}

	pbmp->width = hdr_dibv3.width;
	pbmp->height = hdr_dibv3.height;

	fclose(fp);

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
