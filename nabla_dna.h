#ifndef _NABLA_DNA_H_
#define _NABLA_DNA_H_

#include "ibmp.h"

typedef struct {
	int	size;
	int	*pixels;
} dnabla_t;

extern dnabla_t *build_nabla_dna(ibmp_t *ibmp, int dna_size);
extern int get_n_nabla_pixels(int dna_size);

#endif
