# LFS交叉编译临时工具

使用刚刚构建的交叉工具链对基本工具进行交叉编译。
这些工具会被安装到它们的最终位置，但现在还无法使用。

> 本章应该以用户 lfs 身份完成

```text
su - lfs
```

## 1. M4-1.4.19

M4 软件包包含一个宏处理器

```text
cd $LFS/sources;tar -xf m4-1.4.19.tar.xz;cd m4-1.4.19
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
cd $LFS/sources;tar -xf ncurses-6.5.tar.gz;cd ncurses-6.5
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

```text
time make
```

```text
make DESTDIR=$LFS TIC_PATH=$(pwd)/build/progs/tic install
ln -sv libncursesw.so $LFS/usr/lib/libncurses.so
sed -e 's/^#if.*XOPEN.*$/#if 1/' \
    -i $LFS/usr/include/curses.h
```

## 3. Bash-5.2.37

```text
cd $LFS/sources;tar -xf bash-5.2.37.tar.gz;cd bash-5.2.37
```

```text
./configure --prefix=/usr --build=$(sh support/config.guess) --host=$LFS_TGT --without-bash-malloc
```

```text
time make
```

```text
time make DESTDIR=$LFS install
```

为那些使用 sh 命令运行 shell 的程序考虑，创建一个链接：

```text
ln -sv bash $LFS/bin/sh
```

## 4. Coreutils-9.6

解压源码

```text
cd $LFS/sources;tar -xf coreutils-9.6.tar.xz;cd coreutils-9.6
```

```text
./configure --prefix=/usr                     \
            --host=$LFS_TGT                   \
            --build=$(build-aux/config.guess) \
            --enable-install-program=hostname \
            --enable-no-install-program=kill,uptime
```

```text
time make;time make DESTDIR=$LFS install
```

将程序移动到它们最终安装时的正确位置。在临时环境中这看似不必要，但一些程序会硬编码它们的位置，因此必须进行这步操作：

```text
mv -v $LFS/usr/bin/chroot              $LFS/usr/sbin
mkdir -pv $LFS/usr/share/man/man8
mv -v $LFS/usr/share/man/man1/chroot.1 $LFS/usr/share/man/man8/chroot.8
sed -i 's/"1"/"8"/'                    $LFS/usr/share/man/man8/chroot.8
```

## 5. Diffutils-3.11

```text
cd $LFS/sources;tar -xf diffutils-3.11.tar.xz; cd diffutils-3.11
```

```text
./configure --prefix=/usr   \
            --host=$LFS_TGT \
            --build=$(./build-aux/config.guess)
```

```text
time make;time make DESTDIR=$LFS install
```

## 6. File-5.46

```text
cd $LFS/sources;tar xf file-5.46.tar.gz;cd file-5.46
```

宿主系统 file 命令的版本必须和正在构建的软件包相同，才能在构建过程中创建必要的特征数据文件。运行以下命令，构建 file
命令的一个临时副本：

```text
mkdir build
pushd build
../configure --disable-bzlib      \
--disable-libseccomp \
--disable-xzlib      \
--disable-zlib
make
popd
```

```text
./configure --prefix=/usr --host=$LFS_TGT --build=$(./config.guess)
```

```text
time make FILE_COMPILE=$(pwd)/build/src/file
```

```text
make DESTDIR=$LFS install
```

移除对交叉编译有害的 libtool 档案文件：

```text
rm -v $LFS/usr/lib/libmagic.la
```

## 7. Findutils-4.10.0

```text
cd $LFS/sources;tar -xf findutils-4.10.0.tar.xz;cd findutils-4.10.0
```

```text
./configure --prefix=/usr                   \
            --localstatedir=/var/lib/locate \
            --host=$LFS_TGT                 \
            --build=$(build-aux/config.guess)
```

```text
time make;time make DESTDIR=$LFS install
```

## 8. Gawk-5.3.1

```text
cd $LFS/sources;tar -xf gawk-5.3.1.tar.xz;cd gawk-5.3.1
```

首先，确保不安装某些不需要的文件：

```text
sed -i 's/extras//' Makefile.in
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

## 9. Grep-3.11

```text
cd $LFS/sources;tar -xf grep-3.11.tar.xz;cd grep-3.11
```

```text
./configure --prefix=/usr   \
--host=$LFS_TGT \
--build=$(./build-aux/config.guess)
```

```text
time make;time make DESTDIR=$LFS install
```

## 10. Gzip-1.13

```text
cd $LFS/sources;tar -xf gzip-1.13.tar.xz;cd gzip-1.13
```

```text
./configure --prefix=/usr --host=$LFS_TGT
```

```text
time make;time make DESTDIR=$LFS install
```

## 11. Make-4.4.1

```text
cd $LFS/sources;tar -xf make-4.4.1.tar.gz;cd make-4.4.1
```

```text
./configure --prefix=/usr   \
            --without-guile \
            --host=$LFS_TGT \
            --build=$(build-aux/config.guess)
```

```text
time make;time make DESTDIR=$LFS install
```

## 12. Patch-2.7.6

```text
cd $LFS/sources;tar -xf patch-2.7.6.tar.xz;cd patch-2.7.6
```

```text
./configure --prefix=/usr   \
--host=$LFS_TGT \
--build=$(build-aux/config.guess)
```

```text
time make;time make DESTDIR=$LFS install
```

## 13. Sed-4.9

```text
cd $LFS/sources;tar -xf sed-4.9.tar.xz;cd sed-4.9
```

```text
./configure --prefix=/usr   \
            --host=$LFS_TGT \
            --build=$(./build-aux/config.guess)
```

```text
time make;time make DESTDIR=$LFS install
```

## 14. Tar-1.35

```text
cd $LFS/sources;tar -xf tar-1.35.tar.xz;cd tar-1.35
```

```text
./configure --prefix=/usr                     \
            --host=$LFS_TGT                   \
            --build=$(build-aux/config.guess)
```

```text
time make;time make DESTDIR=$LFS install
```

## 15. Xz-5.6.4

```text
cd $LFS/sources;tar -xf xz-5.6.4.tar.xz;cd xz-5.6.4
```

```text
./configure --prefix=/usr                     \
            --host=$LFS_TGT                   \
            --build=$(build-aux/config.guess) \
            --disable-static                  \
            --docdir=/usr/share/doc/xz-5.6.4
```

```text
time make;time make DESTDIR=$LFS install
```

移除对交叉编译有害的 libtool 档案文件：

```text
rm -v $LFS/usr/lib/liblzma.la
```

## 16. Binutils-2.44 - 第二遍

```text
cd $LFS/sources;rm -rf binutils-2.44;tar -xf binutils-2.44.tar.xz;cd binutils-2.44
```

绕过这个链接到错误库的问题：

```text
sed '6031s/$add_dir//' -i ltmain.sh
```

```text
mkdir -v build;cd build
```

```text
../configure                   \
    --prefix=/usr              \
    --build=$(../config.guess) \
    --host=$LFS_TGT            \
    --disable-nls              \
    --enable-shared            \
    --enable-gprofng=no        \
    --disable-werror           \
    --enable-64-bit-bfd        \
    --enable-new-dtags         \
    --enable-default-hash-style=gnu
```

移除对交叉编译有害的 libtool 档案文件，同时移除不必要的静态库：

```text
time make
```

```text
time make DESTDIR=$LFS install
```

```text
rm -v $LFS/usr/lib/lib{bfd,ctf,ctf-nobfd,opcodes,sframe}.{a,la}
```

## 17. GCC-14.2.0 - 第二遍

在开始构建 GCC 前，记得清除所有覆盖默认优化有关的环境变量

```text
unset CFLAGS CXXFLAGS LDFLAGS CPPFLAGS
```

```text
cd $LFS/sources;rm -rf gcc-14.2.0;tar -xf gcc-14.2.0.tar.xz;cd gcc-14.2.0
```

```text
../configure                                       \
    --build=$(../config.guess)                     \
    --host=$LFS_TGT                                \
    --target=$LFS_TGT                              \
    LDFLAGS_FOR_TARGET=-L$PWD/$LFS_TGT/libgcc      \
    --prefix=/usr                                  \
    --with-build-sysroot=$LFS                      \
    --enable-default-pie                           \
    --enable-default-ssp                           \
    --disable-nls                                  \
    --disable-multilib                             \
    --disable-libatomic                            \
    --disable-libgomp                              \
    --disable-libquadmath                          \
    --disable-libsanitizer                         \
    --disable-libssp                               \
    --disable-libvtv                               \
    --enable-languages=c,c++
```

```text
time make
```

```text
time make DESTDIR=$LFS install
```

运行 cc 可以将选择 C 编译器的权力留给系统管理员：

```text
ln -sv gcc $LFS/usr/bin/cc
```
