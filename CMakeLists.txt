cmake_minimum_required(VERSION 3.28.3)
project(HPC_project C)

set(CMAKE_C_STANDARD 11)

add_executable(HPC_project
        tools/addr.c)
