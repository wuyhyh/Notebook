# LFS交叉编译临时工具

使用刚刚编译的**交叉编译工具**，编译工具并安装到最终位置，虽然暂时还不能使用。

## 1. M4-1.4.19

M4 软件包包含一个宏处理器

```text
tar -xf m4-1.4.19.tar.xz
cd m4-1.4.19
```

```text
./configure --prefix=/usr   \
            --host=$LFS_TGT \
            --build=$(build-aux/config.guess)
```

```text
time make
```

```text
time make DESTDIR=$LFS install
```

## 2. Ncurses-6.5

Ncurses 软件包包含使用时不需考虑终端特性的字符屏幕处理函数库

```text

```

首先，运行以下命令，在宿主系统构建“tic”程序：

```text
mkdir build
pushd build
../configure AWK=gawk
make -C include
make -C progs tic
popd
```

```text
./configure --prefix=/usr                \
            --host=$LFS_TGT              \
            --build=$(./config.guess)    \
            --mandir=/usr/share/man      \
            --with-manpage-format=normal \
            --with-shared                \
            --without-normal             \
            --with-cxx-shared            \
            --without-debug              \
            --without-ada                \
            --disable-stripping          \
            AWK=gawk
```
