# LFS 编译交叉工具链

## 0. 软件包构建过程的概要:

> 对于每个软件包：
>
> 使用 tar 程序，解压需要构建的软件包。解压软件包时，确认您以用户 lfs 的身份登录。
>
> 除了使用 tar 命令解压源码包外，不要使用其他任何将源代码目录树置入工作目录的方法。特别需要注意的是，使用 cp -R
> 从其他位置复制源代码目录树会破坏其中的时间戳，从而导致构建失败。

> a. 切换到解压源码包时产生的目录。
>
> b. 根据指示构建软件包。
>
> c. 构建完成后，切换回包含所有源码包的目录。
>
> d. 除非另有说明，删除解压出来的目录。

## 1. 构建 Binutils-2.44

```text
cd $LFS/sources;tar -xf binutils-2.44.tar.xz;cd binutils-2.44
```

```text
mkdir -v build;cd build
```

```text
time ../configure --prefix=$LFS/tools \
             --with-sysroot=$LFS \
             --target=$LFS_TGT   \
             --disable-nls       \
             --enable-gprofng=no \
             --disable-werror    \
             --enable-new-dtags  \
             --enable-default-hash-style=gnu
```

```text
time make
```

```text
time make install
```

## 2. 构建 GCC-14.2.0 - 第一遍

```text
cd $LFS/sources;tar -xf gcc-14.2.0.tar.xz;cd gcc-14.2.0
```

```text
tar -xf ../mpfr-4.2.1.tar.xz
mv -v mpfr-4.2.1 mpfr
tar -xf ../gmp-6.3.0.tar.xz
mv -v gmp-6.3.0 gmp
tar -xf ../mpc-1.3.1.tar.gz
mv -v mpc-1.3.1 mpc
```

对于 x86_64 平台，还要设置存放 64 位库的默认目录为 “lib”：

```text
case $(uname -m) in
x86_64)
sed -e '/m64=/s/lib64/lib/' \
-i.orig gcc/config/i386/t-linux64
;;
esac
```

```text
mkdir -v build;cd build
```

```text
../configure                  \
    --target=$LFS_TGT         \
    --prefix=$LFS/tools       \
    --with-glibc-version=2.41 \
    --with-sysroot=$LFS       \
    --with-newlib             \
    --without-headers         \
    --enable-default-pie      \
    --enable-default-ssp      \
    --disable-nls             \
    --disable-shared          \
    --disable-multilib        \
    --disable-threads         \
    --disable-libatomic       \
    --disable-libgomp         \
    --disable-libquadmath     \
    --disable-libssp          \
    --disable-libvtv          \
    --disable-libstdcxx       \
    --enable-languages=c,c++
```

```text
time make
```

```text
time make install
```

使用以下命令创建一个完整版本的内部头文件

```text
cd ..
cat gcc/limitx.h gcc/glimits.h gcc/limity.h > \
  $(dirname $($LFS_TGT-gcc -print-libgcc-file-name))/include/limits.h
```

## 3. 安装 Linux-6.13.4 API 头文件

```text
cd $LFS/sources;tar -xf linux-6.13.4.tar.xz;cd linux-6.13.4
```

```text
make mrproper
```

```text
make headers
find usr/include -type f ! -name '*.h' -delete
cp -rv usr/include $LFS/usr
```

## 4. 构建 Glibc-2.41

```text
cd $LFS/sources;tar -xf glibc-2.41.tar.xz;cd glibc-2.41
```

创建一个 LSB 兼容性符号链接

```text
case $(uname -m) in
    i?86)   ln -sfv ld-linux.so.2 $LFS/lib/ld-lsb.so.3
    ;;
    x86_64) ln -sfv ../lib/ld-linux-x86-64.so.2 $LFS/lib64
            ln -sfv ../lib/ld-linux-x86-64.so.2 $LFS/lib64/ld-lsb-x86-64.so.3
    ;;
esac
```

打补丁

```text
patch -Np1 -i ../glibc-2.41-fhs-1.patch
```

```text
mkdir -v build;cd build
```

```text
echo "rootsbindir=/usr/sbin" > configparms
```

```text
../configure                             \
      --prefix=/usr                      \
      --host=$LFS_TGT                    \
      --build=$(../scripts/config.guess) \
      --enable-kernel=5.4                \
      --with-headers=$LFS/usr/include    \
      --disable-nscd                     \
      libc_cv_slibdir=/usr/lib
```

```text
time make
```

```text
time make DESTDIR=$LFS install
```

改正 ldd 脚本中硬编码的可执行文件加载器路径：

```text
sed '/RTLDLIST=/s@/usr@@g' -i $LFS/usr/bin/ldd
```

执行以下命令进行完整性检查：

```text
echo 'int main(){}' | $LFS_TGT-gcc -xc -
readelf -l a.out | grep ld-linux
```

如果一切正常，那么应该没有错误消息，而且最后一行命令应该输出下列格式的内容：

```text
[Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
```

检验步骤顺利完成后，清理测试文件：

```text
rm -v a.out
```

## 5. 构建 GCC-14.2.0 中的 Libstdc++

Libstdc++ 是 GCC 源代码的一部分。您应该先解压 GCC 源码包并切换到解压出来的 gcc-14.2.0 目录

```text
cd $LFS/sources;rm -rf gcc-14.2.0;tar -xf gcc-14.2.0.tar.xz;cd gcc-14.2.0
mkdir -v cpp-build ;cd cpp-build
```

```text
../libstdc++-v3/configure           \
    --host=$LFS_TGT                 \
    --build=$(../config.guess)      \
    --prefix=/usr                   \
    --disable-multilib              \
    --disable-nls                   \
    --disable-libstdcxx-pch         \
    --with-gxx-include-dir=/tools/$LFS_TGT/include/c++/14.2.0
```

```text
time make
```

```text
time make DESTDIR=$LFS install
```

移除对交叉编译有害的 libtool 档案文件：

```text
rm -v $LFS/usr/lib/lib{stdc++{,exp,fs},supc++}.la
```
