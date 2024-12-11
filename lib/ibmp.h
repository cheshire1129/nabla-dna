#ifndef _IBMP_H_
#define _IBMP_H_

#include <stdbool.h>

/* intensity bitmap */
typedef struct {
	int	width, height, channels;
	float	*pixels;
} ibmp_t;

ibmp_t *ibmp_load(const char *fname);
void ibmp_free(ibmp_t *pbmp);

#endif
