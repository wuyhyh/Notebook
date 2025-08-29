# 第一次构建

## 1. 构建 Binutils

```text
tar -xf binutils-2.44.tar.xz
```

```text
cd binutils-2.44;mkdir -v build;cd build
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

## 2. 构建 GCC

```text
tar -xf gcc-14.2.0.tar.xz
```

```text
cd gcc-14.2.0
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

## 3. 安装 linux kernel API

```text
tar -xf linux-6.13.4.tar.xz
cd linux-6.13.4
```

```text
make mrproper
```

```text
make headers
find usr/include -type f ! -name '*.h' -delete
cp -rv usr/include $LFS/usr
```
