cmake_minimum_required(VERSION 3.20)
project(cmatrix_generator)
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake;${CMAKE_MODULE_PATH}")

set(CMAKE_CXX_STANDARD 17)
find_package(TACO REQUIRED)

add_executable(cmatrix_generator main.cpp)

target_compile_features(cmatrix_generator PRIVATE cxx_std_17)
target_link_libraries(cmatrix_generator PRIVATE "TACO::TACO")