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

### 使用 ExternalProject 来集成 Makefile 项目
##include(ExternalProject)
##
##ExternalProject_Add(
##        stack_v3
##        PREFIX ${CMAKE_BINARY_DIR}/_deps
##        SOURCE_DIR ${PROJECT_SOURCE_DIR}/Code/stack_v3
###        CMAKE_ARGS -DCMAKE_INSTALL_PREFIX=<install_path>  # 如果有安装路径，可以在此处设置
##        BUILD_COMMAND ${CMAKE_MAKE_PROGRAM}  # 确保使用正确的 make 命令
##        INSTALL_COMMAND ""  # 没有安装步骤，保持为空
##        BUILD_ALWAYS 1      # 每次都重新构建
##        CONFIGURE_COMMAND ""  # 不需要 CMake 配置步骤
##        BUILD_COMMAND ${CMAKE_MAKE_PROGRAM}  # 使用 make 构建
##        INSTALL_COMMAND ""  # 省略安装步骤
##        LOG_DOWNLOAD ON  # 启用下载日志，查看下载过程
##        LOG_BUILD ON  # 启用构建日志，查看构建过程
##)
