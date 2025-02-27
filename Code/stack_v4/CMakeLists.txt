# 设置当前目录的源文件
set(SOURCES
        stack_client.c
        stackADT.c
)

# 如果有头文件，可以定义它们，通常不需要添加到 CMake 文件
set(HEADERS
        stackADT.h
)

# 创建可执行文件
add_executable(stack_executable_v4 ${SOURCES} ${HEADERS})
