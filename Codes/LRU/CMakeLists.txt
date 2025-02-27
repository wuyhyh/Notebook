# 设置 CMake 的最低版本
cmake_minimum_required(VERSION 3.10)

# 设置项目名称
project(LRU_Cache)

# 设置 C 标准
set(CMAKE_C_STANDARD 99)

# 添加可执行文件
add_executable(lru_test hash.c lru.c lru_test.c)

# 如果有特定的编译选项，可以在这里添加
# target_compile_options(lru_test PRIVATE -Wall)

# 如果你使用的库有其他依赖，可以链接到这里
# target_link_libraries(lru_test some_library)

