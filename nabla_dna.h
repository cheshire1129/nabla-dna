#ifndef _NABLA_DNA_H_
#define _NABLA_DNA_H_

#include <stdint.h>

#include "ibmp.h"

typedef struct {
	int	size;
	uint8_t	*pixels;
} dnabla_t;

extern dnabla_t *build_nabla_dna(ibmp_t *ibmp, int dna_size);
extern int get_n_nabla_pixels(int dna_size);
extern void free_dnabla(dnabla_t *dnabla);

#endif
