cmake_minimum_required(VERSION 3.16)

project(nabla-dna VERSION 0.0.1)

configure_file(config.h.in config.h)

file(GLOB SRC_MKDNA "src/mkdna/*.c")

add_executable(mkdna ${SRC_MKDNA})

target_include_directories(mkdna PUBLIC "${PROJECT_BINARY_DIR}")

target_link_libraries(mkdna PUBLIC libm.so)

