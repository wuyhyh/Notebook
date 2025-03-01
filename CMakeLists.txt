cmake_minimum_required(VERSION 3.10)

# 设置项目名称
project(Notebook)

# 设置 C 标准
set(CMAKE_C_STANDARD 99)

# 添加 lru 子目录，CMake 会自动处理该目录中的 CMakeLists.txt
add_subdirectory(Code/lru)

# 如果以后有其他子目录，按以下方式继续添加：
# add_subdirectory(Code/another_subdir)
add_subdirectory(Code/stack)
add_subdirectory(Code/stack_v3)
add_subdirectory(Code/stack_v4)
add_subdirectory(Code/stack_v5_array)
add_subdirectory(Code/stack_v5_link)

# leetcode
add_subdirectory(LeetCode/Interview/160寻找两个链表的交点)
add_subdirectory(LeetCode/Interview/148排序链表)
