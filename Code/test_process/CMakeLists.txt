# 设置当前目录的源文件
set(SOURCES
        test_process.c
)

# 如果有头文件，可以定义它们，通常不需要添加到 CMake 文件
#set(HEADERS
#        stackADT.h
#)

# 创建可执行文件
add_executable(test_process_executable ${SOURCES} ${HEADERS})
