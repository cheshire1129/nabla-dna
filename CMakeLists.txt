cmake_minimum_required(VERSION 3.16)

project(nabla-dna VERSION 0.0.1)

configure_file(config.h.in config.h)

add_executable(mkdna mkdna.c ibmp.c xbmp.c nabla_dna.c)

target_include_directories(mkdna PUBLIC "${PROJECT_BINARY_DIR}")

target_link_libraries(mkdna PUBLIC libm.so)

