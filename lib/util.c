#include "config.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

void
errmsg(const char *fmt, ...)
{
        va_list ap;
        char    *errmsg;

        va_start(ap, fmt);
        vasprintf(&errmsg, fmt, ap);
        va_end(ap);

        fprintf(stderr, "ERROR: %s\n", errmsg);

        free(errmsg);
}
