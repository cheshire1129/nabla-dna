cmake_minimum_required(VERSION 3.16)

project(nabla-dna VERSION 0.0.1)

configure_file(config.h.in config.h)

file(GLOB SRC_LIB "lib/*.c")

add_library(nabla STATIC ${SRC_LIB})

target_include_directories(nabla PUBLIC "${PROJECT_BINARY_DIR}")

file(GLOB SRC_MKDNA "src/mkdna/*.c")

add_executable(mkdna ${SRC_MKDNA})

target_include_directories(mkdna PRIVATE "lib" "${PROJECT_BINARY_DIR}")

target_link_libraries(mkdna PRIVATE nabla m)

