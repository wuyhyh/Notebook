all:
	mkdir -p bin/
	gcc -fPIC -c src/tree.c -o bin/tree.o
	gcc -fPIC -c src/queue.c -o bin/queue.o
	gcc -fPIC -c src/width.c -o bin/width.o

	# 生成动态链接库
	gcc -shared -o bin/libwidth.so bin/width.o bin/tree.o bin/queue.o

	# 编译测试程序
	gcc -o bin/test_width src/test_width.c -Lbin -lwidth -I./src -Wl,-rpath,bin

clean:
	rm -rf bin/test_width bin/libwidth.so bin/*.o
	rm -rf bin/
