cmake_minimum_required(VERSION 3.10)
project(AlgebraicLayouts CXX)

add_executable(test-swizzle tests/test-swizzle.cpp)
target_include_directories(test-swizzle PRIVATE include)
target_compile_features(test-swizzle PRIVATE cxx_std_20)
