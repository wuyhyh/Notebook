all:
	mkdir -p bin/
	gcc -g -fPIC -c src/tree.c -o bin/tree.o
	gcc -g -fPIC -c src/queue.c -o bin/queue.o
	gcc -g -fPIC -c src/width.c -o bin/width.o

	# 生成动态链接库
	gcc -g -shared -o bin/libwidth.so bin/width.o bin/tree.o bin/queue.o

	# 编译测试程序
	#gcc -o bin/test_width src/test_width.c -Lbin -lwidth -I./src -Wl,-rpath,'$ORIGIN'
	gcc -g -o bin/test_width src/test_width.c -Lbin -lwidth -I./src -Wl,-rpath,\$$ORIGIN


clean:
	rm -rf bin/test_width bin/libwidth.so bin/*.o
	rm -rf bin/
