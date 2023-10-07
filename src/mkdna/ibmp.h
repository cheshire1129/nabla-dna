#ifndef _IBMP_H_
#define _IBMP_H_

#include <stdbool.h>

/* This code is referenced from https://github.com/draekko/libbitmap */

/* intensity bitmap */
typedef struct {
	int	width, height;
	float	*pixels;
} ibmp_t;

ibmp_t *ibmp_load(const char *fname);
void ibmp_free(ibmp_t *pbmp);

#endif
