cmake_minimum_required(VERSION 3.16)

project(nabla-dna VERSION 0.0.1)

configure_file(config.h.in config.h)

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall")
endif()

find_package(OpenMP REQUIRED)
find_package(BLAS REQUIRED)

file(GLOB SRC_LIB "lib/*.c")

add_library(nabla STATIC ${SRC_LIB})

target_include_directories(nabla PUBLIC "${PROJECT_BINARY_DIR}")

file(GLOB SRC_MKDNA "src/mkdna/*.c")

add_executable(mkdna ${SRC_MKDNA})

target_include_directories(mkdna PRIVATE "lib" "${PROJECT_BINARY_DIR}")

target_link_libraries(mkdna PRIVATE nabla m)

file(GLOB SRC_MKDB "src/mkdb/*.c" src/mkdb/vdb.cxx)

add_executable(mkdb ${SRC_MKDB})

target_include_directories(mkdb PRIVATE "lib" "${PROJECT_BINARY_DIR}")

target_link_libraries(mkdb PRIVATE nabla faiss OpenMP::OpenMP_C BLAS::BLAS stdc++ m)

