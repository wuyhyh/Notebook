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

# 设置其他可执行文件（例如项目的主入口）
# add_executable(NotebookExecutable Code/main.c)
