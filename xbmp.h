#ifndef _XBMP_H_
#define _XBMP_H_

#include "ibmp.h"

/* averaged bitmap or nabla bitmap */
typedef struct {
	int	size;
	float	*pixels;
} xbmp_t;

xbmp_t *build_nabla_bmp(ibmp_t *ibmp, int dna_size);
void free_xbmp(xbmp_t *xbmp);

int get_n_nabla_pixels(int dna_size);

#endif
