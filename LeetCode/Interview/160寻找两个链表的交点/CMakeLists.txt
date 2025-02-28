# 设置当前目录的源文件
set(SOURCES
        intersection.c
)

# 如果有头文件，可以定义它们，通常不需要添加到 CMake 文件
set(HEADERS
)

# 创建可执行文件
add_executable(intersection ${SOURCES} ${HEADERS})

# 如果需要链接其他的库，可以在这里添加
# target_link_libraries(lruExecutable some_other_library)

# 如果需要设置包含目录，例如头文件的路径
# target_include_directories(lruExecutable PUBLIC ${PROJECT_SOURCE_DIR}/include)
