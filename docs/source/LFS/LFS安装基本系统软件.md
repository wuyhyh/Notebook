# LFS 安装基本系统软件

## 0. 首先进入 chroot

```text
mkdir -pv $LFS/{dev,proc,sys,run}
mount -v --bind /dev $LFS/dev
mount -vt devpts devpts -o gid=5,mode=0620 $LFS/dev/pts
mount -vt proc proc $LFS/proc
mount -vt sysfs sysfs $LFS/sys
mount -vt tmpfs tmpfs $LFS/run
if [ -h $LFS/dev/shm ]; then
install -v -d -m 1777 $LFS$(realpath /dev/shm)
else
mount -vt tmpfs -o nosuid,nodev tmpfs $LFS/dev/shm
fi
chroot "$LFS" /usr/bin/env -i   \
HOME=/root                  \
TERM="$TERM"                \
PS1='(lfs chroot) \u:\w\$ ' \
PATH=/usr/bin:/usr/sbin     \
MAKEFLAGS="-j$(nproc)"      \
TESTSUITEFLAGS="-j$(nproc)" \
/bin/bash --login
```

## 1. Man-pages-6.12

```text
cd /sources;tar -xf man-pages-6.12.tar.xz;cd man-pages-6.12
```

移除描述密码散列函数的两个手册页。Libxcrypt 会提供这些手册页的更好版本。

```text
rm -v man3/crypt*
```

执行以下命令安装 Man-pages：

```text
time make -R GIT=false prefix=/usr install
```

## 2. Iana-Etc-20250123

Iana-Etc 软件包包含网络服务和协议的数据

```text
cd /sources;tar -xf iana-etc-20250123.tar.gz;cd iana-etc-20250123
```

安装 Iana-Etc
对于该软件包，我们只需要将文件复制到正确的位置：

```text
cp -v services protocols /etc
```

## 3. Glibc-2.41

Glibc 软件包包含主要的 C 语言库。它提供用于分配内存、检索目录、打开和关闭文件、读写文件、字符串处理、模式匹配、算术等用途的基本子程序。

### 3.1 安装 Glibc

```text
cd /sources;rm -rf glibc-2.41;tar -xf glibc-2.41.tar.xz;cd glibc-2.41
```

应用一个补丁，使得这些程序在 FHS 兼容的位置存放运行时数据：

```text
patch -Np1 -i ../glibc-2.41-fhs-1.patch
```

Glibc 文档推荐在一个新建的目录中构建 Glibc：

```text
mkdir -v build;cd build
```

确保将 ldconfig 和 sln 工具安装到 /usr/sbin 目录中：

```text
echo "rootsbindir=/usr/sbin" > configparms
```

准备编译 Glibc：

```text
../configure --prefix=/usr               \
--disable-werror                         \
--enable-kernel=5.4                      \
--enable-stack-protector=strong          \
--disable-nscd                           \
libc_cv_slibdir=/usr/lib
```

编译

```text
time make
```

Glibc 的测试套件十分关键。在任何情况下都不要跳过它。

通常来说，可能会有极少数测试不能通过，下面列出的失败结果一般可以安全地忽略。
执行以下命令进行测试：

```text
time make check
```

安装该软件包：

```text
time make install
```

改正 ldd 脚本中硬编码的可执行文件加载器路径：

```text
sed '/RTLDLIST=/s@/usr@@g' -i /usr/bin/ldd
```

以下命令将会安装能够覆盖测试所需的最小 locale 集合：

```text
localedef -i C -f UTF-8 C.UTF-8
localedef -i cs_CZ -f UTF-8 cs_CZ.UTF-8
localedef -i de_DE -f ISO-8859-1 de_DE
localedef -i de_DE@euro -f ISO-8859-15 de_DE@euro
localedef -i de_DE -f UTF-8 de_DE.UTF-8
localedef -i el_GR -f ISO-8859-7 el_GR
localedef -i en_GB -f ISO-8859-1 en_GB
localedef -i en_GB -f UTF-8 en_GB.UTF-8
localedef -i en_HK -f ISO-8859-1 en_HK
localedef -i en_PH -f ISO-8859-1 en_PH
localedef -i en_US -f ISO-8859-1 en_US
localedef -i en_US -f UTF-8 en_US.UTF-8
localedef -i es_ES -f ISO-8859-15 es_ES@euro
localedef -i es_MX -f ISO-8859-1 es_MX
localedef -i fa_IR -f UTF-8 fa_IR
localedef -i fr_FR -f ISO-8859-1 fr_FR
localedef -i fr_FR@euro -f ISO-8859-15 fr_FR@euro
localedef -i fr_FR -f UTF-8 fr_FR.UTF-8
localedef -i is_IS -f ISO-8859-1 is_IS
localedef -i is_IS -f UTF-8 is_IS.UTF-8
localedef -i it_IT -f ISO-8859-1 it_IT
localedef -i it_IT -f ISO-8859-15 it_IT@euro
localedef -i it_IT -f UTF-8 it_IT.UTF-8
localedef -i ja_JP -f EUC-JP ja_JP
localedef -i ja_JP -f SHIFT_JIS ja_JP.SJIS 2> /dev/null || true
localedef -i ja_JP -f UTF-8 ja_JP.UTF-8
localedef -i nl_NL@euro -f ISO-8859-15 nl_NL@euro
localedef -i ru_RU -f KOI8-R ru_RU.KOI8-R
localedef -i ru_RU -f UTF-8 ru_RU.UTF-8
localedef -i se_NO -f UTF-8 se_NO.UTF-8
localedef -i ta_IN -f UTF-8 ta_IN.UTF-8
localedef -i tr_TR -f UTF-8 tr_TR.UTF-8
localedef -i zh_CN -f GB18030 zh_CN.GB18030
localedef -i zh_HK -f BIG5-HKSCS zh_HK.BIG5-HKSCS
localedef -i zh_TW -f UTF-8 zh_TW.UTF-8
```

本章中后续的一些测试可能需要安装两个 locale：

```text
localedef -i C -f UTF-8 C.UTF-8
localedef -i ja_JP -f SHIFT_JIS ja_JP.SJIS 2> /dev/null || true
```

### 3.2 配置 Glibc

#### 3.2.1 创建 nsswitch.conf

由于 Glibc 的默认值在网络环境下不能很好地工作，需要创建配置文件 /etc/nsswitch.conf。

执行以下命令创建新的 /etc/nsswitch.conf：

```text
cat > /etc/nsswitch.conf << "EOF"
# Begin /etc/nsswitch.conf

passwd: files systemd
group: files systemd
shadow: files systemd

hosts: mymachines resolve [!UNAVAIL=return] files myhostname dns
networks: files

protocols: files
services: files
ethers: files
rpc: files

# End /etc/nsswitch.conf
EOF
```

#### 3.2.2 添加时区数据

输入以下命令，安装并设置时区数据：

```text
tar -xf ../../tzdata2025a.tar.gz

ZONEINFO=/usr/share/zoneinfo
mkdir -pv $ZONEINFO/{posix,right}

for tz in etcetera southamerica northamerica europe africa antarctica  \
asia australasia backward; do
zic -L /dev/null   -d $ZONEINFO       ${tz}
zic -L /dev/null   -d $ZONEINFO/posix ${tz}
zic -L leapseconds -d $ZONEINFO/right ${tz}
done

cp -v zone.tab zone1970.tab iso3166.tab $ZONEINFO
zic -d $ZONEINFO -p America/New_York
unset ZONEINFO tz
```

一种确定本地时区的方法是运行脚本：

```text
tzselect
```

持久化时区

```text
export TZ='Asia/Shanghai'
```

确定时区后，执行以下命令，创建 /etc/localtime：

```text
ln -sfv /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```

#### 3.2.3 配置动态加载器

默认情况下，动态加载器 (/lib/ld-linux.so.2) 在 /usr/lib 中搜索程序运行时需要的动态库。

然而，如果在除了 /usr/lib 以外的其他目录中有动态库，为了使动态加载器能够找到它们，需要把这些目录添加到文件 /etc/ld.so.conf
中。

有两个目录 /usr/local/lib 和 /opt/lib 经常包含附加的共享库，所以现在将它们添加到动态加载器的搜索目录中。

运行以下命令，创建一个新的 /etc/ld.so.conf：

```text
cat > /etc/ld.so.conf << "EOF"
# Begin /etc/ld.so.conf
/usr/local/lib
/opt/lib

EOF
```

> 如果希望的话，动态加载器也可以搜索一个目录，并将其中的文件包含在 ld.so.conf
> 中。通常包含文件目录中的文件只有一行，指定一个期望的库文件目录。如果需要这项功能，执行以下命令：
>
> ```text
> cat >> /etc/ld.so.conf << "EOF"
> # Add an include directory
> include /etc/ld.so.conf.d/*.conf
>
> EOF
> mkdir -pv /etc/ld.so.conf.d
> ```

## 4. Zlib-1.3.1

Zlib 软件包包含一些程序使用的压缩和解压缩子程序。

```text
cd /sources;tar -xf zlib-1.3.1.tar.gz;cd zlib-1.3.1
```

准备编译 Zlib：

```text
./configure --prefix=/usr
```

编译该软件包：

```text
time make
```

运行命令以测试编译结果：

```text
time make check
```

安装该软件包：

```text
time make install
```

删除无用的静态库：

```text
rm -fv /usr/lib/libz.a
```

## 5. Bzip2-1.0.8

Bzip2 软件包包含用于压缩和解压缩文件的程序。

使用 bzip2 压缩文本文件可以获得比传统的 gzip 优秀许多的压缩比。

```text
cd /sources;tar -xf bzip2-1.0.8.tar.gz;cd bzip2-1.0.8
```

安装 Bzip2
应用一个补丁，以安装该软件包的文档：

```text
patch -Np1 -i ../bzip2-1.0.8-install_docs-1.patch
```

以下命令保证安装的符号链接是相对的：

```text
sed -i 's@\(ln -s -f \)$(PREFIX)/bin/@\1@' Makefile
```

确保手册页被安装到正确位置：

```text
sed -i "s@(PREFIX)/man@(PREFIX)/share/man@g" Makefile
```

执行以下命令，准备编译 Bzip2：

```text
make -f Makefile-libbz2_so
make clean
```

编译并测试该软件包：

```text
time make
```

安装软件包中的程序：

```text
make PREFIX=/usr install
```

安装共享库：

```text
cp -av libbz2.so.* /usr/lib
ln -sv libbz2.so.1.0.8 /usr/lib/libbz2.so
```

安装链接到共享库的 bzip2 二进制程序到 /bin 目录，并将两个和 bzip2 完全相同的文件替换成符号链接：

```text
cp -v bzip2-shared /usr/bin/bzip2
for i in /usr/bin/{bzcat,bunzip2}; do
ln -sfv bzip2 $i
done
```

删除无用的静态库：

```text
rm -fv /usr/lib/libbz2.a
```

## 6. Xz-5.6.4

Xz 软件包包含文件压缩和解压缩工具，它能够处理 lzma 和新的 xz 压缩文件格式。
使用 xz 压缩文本文件，可以得到比传统的 gzip 或 bzip2 更好的压缩比。

```text
cd /sources;rm -rf xz-5.6.4;tar -xf xz-5.6.4.tar.xz;cd xz-5.6.4
```

准备编译 Xz：

```text
./configure --prefix=/usr    \
--disable-static \
--docdir=/usr/share/doc/xz-5.6.4
```

编译该软件包：

```text
time make
```

运行命令以测试编译结果：

```text
make check
```

安装该软件包：

```text
make install
```

## 7. Lz4-1.10.0

Lz4 是一种无损压缩算法，其压缩速率可达每 CPU 核心 500 MB/s。

它的优势是解压缩非常快，速率高达每 CPU 核心若干 GB/s。
Lz4 可以和 Zstandard 共同使用以达到更高的压缩速率。

安装 Lz4

```text
cd /sources;tar -xf lz4-1.10.0.tar.gz;cd lz4-1.10.0
```

编译该软件包：

```text
time make BUILD_STATIC=no PREFIX=/usr
```

运行命令以测试编译结果：

```text
make -j1 check
```

安装该软件包：

```text
make BUILD_STATIC=no PREFIX=/usr install
```

## 8. Zstd-1.5.7

Zstandard 是一种实时压缩算法，提供了较高的压缩比。

它具有很宽的压缩比/速度权衡范围，同时支持具有非常快速的解压缩。

安装 Zstd

```text
cd /sources;tar -xf zstd-1.5.7.tar.gz;cd zstd-1.5.7
```

编译该软件包：

```text
time make prefix=/usr
```

> 注意
> 在输出的测试结果中，可能会出现 'failed'。
>
> 这是正常的，只有 'FAIL' 才表示测试失败。该软件包的测试应该能够全部通过。

运行命令以测试编译结果：

```text
make check
```

安装该软件包：

```text
make prefix=/usr install
```

删除静态库：

```text
rm -v /usr/lib/libzstd.a
```

## 9. File-5.46

File 软件包包含用于确定给定文件类型的工具。

安装 File

```text
cd /sources;rm -rf file-5.46;tar -xf file-5.46.tar.gz;cd file-5.46
```

准备编译 File：

```text
./configure --prefix=/usr
```

编译该软件包：

```text
time make
```

运行命令以测试编译结果：

```text
make check
```

安装该软件包：

```text
make install
```

## 10. Readline-8.2.13

Readline 软件包包含一些提供命令行编辑和历史记录功能的库。

安装 Readline

```text
cd /sources;tar -xf readline-8.2.13.tar.gz;cd readline-8.2.13
```

重新安装 Readline 会导致旧版本的库被重命名为 <库名称>.old。这一般不是问题，但某些情况下会触发 ldconfig 的一个链接
bug。运行下面的两条 sed 命令防止这种情况：

```text
sed -i '/MV.*old/d' Makefile.in
sed -i '/{OLDSUFF}/c:' support/shlib-install
```

下面防止在共享库中硬编码库文件搜索路径 (rpath)。
该软件包在安装到标准位置时并不需要 rpath，而且 rpath
在一些情况下会产生我们不希望的副作用，甚至导致安全问题：

```text
sed -i 's/-Wl,-rpath,[^ ]*//' support/shobj-conf
```

准备编译 Readline：

```text
./configure --prefix=/usr    \
--disable-static \
--with-curses    \
--docdir=/usr/share/doc/readline-8.2.13
```

编译该软件包：

```text
time make SHLIB_LIBS="-lncursesw"
```

该软件包不包含测试套件。

安装该软件包：

```text
make install
```

安装该软件包的文档：

```text
install -v -m644 doc/*.{ps,pdf,html,dvi} /usr/share/doc/readline-8.2.13
```

## 11. M4-1.4.19

M4 软件包包含一个宏处理器。

安装 M4

```text
cd /sources;rm -rf m4-1.4.19;tar -xf m4-1.4.19.tar.xz;cd m4-1.4.19
```

准备编译 M4：

```text
./configure --prefix=/usr
```

编译该软件包：

```text
time make
```

运行命令以测试编译结果：

```text
make check
```

安装该软件包：

```text
make install
```

## 12. Bc-7.0.3

Bc 软件包包含一个任意精度数值处理语言。

安装 Bc

```text
cd /sources;tar -xf bc-7.0.3.tar.xz;cd bc-7.0.3
```

准备编译 Bc：

```text
CC=gcc ./configure --prefix=/usr -G -O3 -r
```

编译该软件包：

```text
time make
```

为了测试 bc，运行：

```text
make test
```

安装该软件包：

```text
make install
```

## 13. 



