cmake_minimum_required(VERSION 3.20)
project(cmatrix_generator)

set(CMAKE_CXX_STANDARD 17)

add_executable(cmatrix_generator main.cpp)

target_compile_features(cmatrix_generator PRIVATE cxx_std_17)