#include "config.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <dirent.h>
#include <stdbool.h>

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

bool
is_file(const char *path)
{
	struct stat	st;

	if (stat(path, &st) < 0)
		return false;
	if (S_ISDIR(st.st_mode))
		return true;
	return false;
}

bool
is_folder(const char *path)
{
	struct stat	st;

	if (stat(path, &st) < 0)
		return false;
	if (S_ISDIR(st.st_mode))
		return true;
	return false;
}

void *
lib_opendir(const char *path)
{
	return opendir(path);
}

const char *
lib_readdir(void *dir)
{
	struct dirent	*ent;

retry:
	ent = readdir(dir);
	if (ent == NULL)
		return NULL;
	if (ent->d_name[0] == '.') {
		if (ent->d_name[1] == '\0')
			goto retry;
		if (ent->d_name[1] == '.' && ent->d_name[2] == '\0')
			goto retry;
	}
	return ent->d_name;
}

void
lib_closedir(void *dir)
{
	closedir(dir);
}

typedef struct {
	FILE	*fp;
	char	buf[4096];
} lst_t;

void *
lib_openlst(const char *path)
{
	FILE	*fp;
	lst_t	*lst;

	if ((fp = fopen(path, "r")) == NULL)
		return NULL;
	lst = (lst_t *)malloc(sizeof(lst_t));
	if (lst == NULL) {
		fclose(fp);
		return NULL;
	}

	lst->fp = fp;

	return lst;
}

const char *
lib_readlst(void *_lst)
{
	lst_t	*lst = (lst_t *)_lst;
	char	buf[4096];

again:
	if (fgets(buf, sizeof(buf), lst->fp) == NULL)
		return NULL;
	if (buf[0] == '#')
		goto again;
	if (sscanf(buf, "%s", lst->buf) != 1)
		goto again;
	return lst->buf;
}

void
lib_closelst(void *_lst)
{
	lst_t	*lst = (lst_t *)_lst;

	fclose(lst->fp);
	free(lst);
}

bool
path_exist(const char *path)
{
	if (access(path, F_OK) == 0)
		return true;
	return false;
}

bool
path_has_ext(const char *path, const char *ext)
{
	const char	*dot = strrchr(path, '.');

	if (strcmp(dot + 1, ext) == 0)
		return true;
	return false;
}

char *
path_join(const char *path, const char *fname)
{
	char	*joined;

	asprintf(&joined, "%s/%s", path, fname);
	return joined;
}

char *
path_build(const char *path_folder, const char *name, const char *ext)
{
	char	*builded;

	if (path_folder)
		asprintf(&builded, "%s/%s.%s", path_folder, name, ext);
	else
		asprintf(&builded, "%s.%s", name, ext);
	return builded;
}

char *
path_get_replaced_ext(const char *path, const char *ext_new)
{
	char	*path_new;
	const char	*dot = strrchr(path, '.');

	if (dot) {
		asprintf(&path_new, "%s.%s", path, ext_new);
		sprintf(path_new + (dot - path) + 1, "%s", ext_new);
	} else {
		asprintf(&path_new, "%s.%s", path, ext_new);
	}

	return path_new;
}
