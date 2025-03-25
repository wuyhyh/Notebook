# Read kernel source code in CLion IDE on Ubuntu 24.04

使用CLion阅读某个版本的内核源码，编译生成compile_database.json项目

```shell
git checkout -b v6.12
git reset --hard v6.12
bear --version
make defconfig
bear -- make -j${nproc}
```
