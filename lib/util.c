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
lib_iterlst(const char *path_list, bool (*func)(unsigned int, const char *, void *), void *ctx)
{
	void	*lst;
	const char	*img_name;
	unsigned int	idx;

	if ((lst = lib_openlst(path_list)) == NULL)
		return false;

	idx = 0;
	while ((img_name = lib_readlst(lst))) {
		if (!func(idx, img_name, ctx)) {
			lib_closelst(lst);
			return false;
		}
		idx++;
	}
	lib_closelst(lst);
	return true;
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

	if (dot == NULL)
		return false;
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

const char *
path_basename(const char *path)
{
	char	*path_base;
	char	*slash;

	slash = strrchr(path, '/');
	if (slash == NULL)
		return path;
	return slash + 1;
}

bool
try_iter_imgfmts(const char *img_folder, const char *imgname, bool (*func)(const char *, void *), void *ctx)
{
	const char	*ext_names[] = { "jpg", "png", "gif", "bmp", "jpeg", "JPG", "PNG", "GIF", "BMP", "JPEG" };
	int	i;

	if (path_exist(imgname))
		return func(imgname, ctx);
	for (i = 0; i < sizeof(ext_names) / sizeof(const char *); i++) {
		char	*imgpath = path_build(img_folder, imgname, ext_names[i]);
		if (path_exist(imgpath)) {
			bool	res = func(imgpath, ctx);
			free(imgpath);
			return res;
		}
		free(imgpath);
	}
	return false;
}

bool
iter_folder(const char *path_folder, bool (*func)(const char *, const char *, void *), void *ctx)
{
	const char	*name;
	void	*dir;
	bool	res = true;

	dir = lib_opendir(path_folder);
	if (dir == NULL)
		return false;

	while (res && (name = lib_readdir(dir))) {
		char	*path;

		path = path_join(path_folder, name);
		res = func(name, path, ctx);
		free(path);
	}

	lib_closedir(dir);

	return res;
}
