#ifndef _UTIL_H_
#define _UTIL_H_

#include <stdbool.h>

void errmsg(const char *fmt, ...);
bool is_file(const char *path);
bool is_folder(const char *path);

void *lib_opendir(const char *path);
const char *lib_readdir(void *dir);
void lib_closedir(void *dir);

void *lib_openlst(const char *path);
const char *lib_readlst(void *lst);
void lib_closelst(void *lst);
int lib_iterlst(const char *path_list, bool (*func)(unsigned int, const char *, void *), void *ctx);

char *path_exist(const char *path);
char *path_join(const char *path, const char *fname);
char *path_build(const char *folder, const char *name, const char *ext);
char *path_get_replaced_ext(const char *path, const char *ext_new);
bool path_has_ext(const char *path, const char *ext);
const char *path_basename(const char *path);

bool
try_iter_imgfmts(const char *img_folder, const char *imgname, bool (*func)(const char *, void *), void *ctx);
bool
iter_folder(const char *path_folder, bool (*func)(const char *, const char *, void *), void *ctx);

void init_tickcount(void);
unsigned long get_tickcount(void);

#endif
