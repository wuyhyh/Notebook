# LFS 安装基本系统软件 Part1

在本章中，我们将真正开始构造 LFS 系统。

一般来说，LFS 作者不鼓励构建和安装静态库。
在现代 Linux 系统中，多数静态库已经失去存在的意义。
另外，将静态库链接到程序中可能是有害的。

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
../configure --prefix=/usr                            \
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

修改 Makefile，跳过一个过时的，对于现代的 Glibc 构型会失败的完整性检查：

```text
sed '/test-installation/s@$(PERL)@echo not running@' -i ../Makefile
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

## 13. Flex-2.6.4

Flex 软件包包含一个工具，用于生成在文本中识别模式的程序。

安装 Flex

```text
cd /sources;tar -xf flex-2.6.4.tar.gz;cd flex-2.6.4
```

准备编译 Flex：

```text
./configure --prefix=/usr                      \
            --docdir=/usr/share/doc/flex-2.6.4 \
            --disable-static
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

个别程序还不知道 flex，并试图去运行它的前身 lex。
为了支持这些程序，创建一个名为 lex 的符号链接，它运行 flex 并启动其模拟 lex 的模式，
同时将 lex 的手册页也创建为符号链接：

```text
ln -sv flex   /usr/bin/lex
ln -sv flex.1 /usr/share/man/man1/lex.1
```

## 14. Tcl-8.6.16

Tcl 软件包包含工具命令语言，它是一个可靠的通用脚本语言。Expect 软件包是用 Tcl (读作“tickle”) 编写的。

安装 Tcl

```text
cd /sources;tar -xf tcl8.6.16-src.tar.gz;cd tcl8.6.16
```

为了支持 Binutils，GCC，以及其他一些软件包测试套件的运行，需要安装这个软件包和接下来的两个 (Expect 与 DejaGNU)。

为了测试目的安装三个软件包看似浪费，但是只有运行了测试，才能放心地确定多数重要工具可以正常工作，即使测试不是必要的。

我们必须安装这些软件包，才能执行本章中的测试套件。

准备编译 Tcl：

```text
SRCDIR=$(pwd)
cd unix
./configure --prefix=/usr           \
            --mandir=/usr/share/man \
            --disable-rpath
```

构建该软件包：

```text
make

sed -e "s|$SRCDIR/unix|/usr/lib|" \
    -e "s|$SRCDIR|/usr/include|"  \
    -i tclConfig.sh

sed -e "s|$SRCDIR/unix/pkgs/tdbc1.1.10|/usr/lib/tdbc1.1.10|" \
    -e "s|$SRCDIR/pkgs/tdbc1.1.10/generic|/usr/include|"    \
    -e "s|$SRCDIR/pkgs/tdbc1.1.10/library|/usr/lib/tcl8.6|" \
    -e "s|$SRCDIR/pkgs/tdbc1.1.10|/usr/include|"            \
    -i pkgs/tdbc1.1.10/tdbcConfig.sh

sed -e "s|$SRCDIR/unix/pkgs/itcl4.3.2|/usr/lib/itcl4.3.2|" \
    -e "s|$SRCDIR/pkgs/itcl4.3.2/generic|/usr/include|"    \
    -e "s|$SRCDIR/pkgs/itcl4.3.2|/usr/include|"            \
    -i pkgs/itcl4.3.2/itclConfig.sh

unset SRCDIR
```

`make`命令之后的若干“sed”命令从配置文件中删除构建目录，并用安装目录替换它们

运行命令以测试编译结果：

```text
make test
```

安装该软件包：

```text
make install
```

将安装好的库加上写入权限，以便将来移除调试符号：

```text
chmod -v u+w /usr/lib/libtcl8.6.so
```

安装 Tcl 的头文件。下一个软件包 Expect 需要它们才能构建。

```text
make install-private-headers
```

创建一个必要的符号链接：

```text
ln -sfv tclsh8.6 /usr/bin/tclsh
```

重命名一个与 Perl 手册页文件名冲突的手册页：

```text
mv /usr/share/man/man3/{Thread,Tcl_Thread}.3
```

如果需要，可以运行以下命令安装文档：

```text
cd ..
tar -xf ../tcl8.6.16-html.tar.gz --strip-components=1
mkdir -v -p /usr/share/doc/tcl-8.6.16
cp -v -r  ./html/* /usr/share/doc/tcl-8.6.16
```

## 15 Expect-5.45.4

Expect 软件包包含通过脚本控制的对话，自动化 telnet，ftp，passwd，fsck，rlogin，以及 tip 等交互应用的工具。Expect
对于测试这类程序也很有用，它简化了这类通过其他方式很难完成的工作。DejaGnu 框架是使用 Expect 编写的。

安装 Expect

```text
cd /sources;tar -xf expect5.45.4.tar.gz;cd expect5.45.4
```

Expect 需要伪终端 (PTY) 才能正常工作。进行简单测试以验证 PTY 是否在 chroot 环境中正常工作：

```text
python3 -c 'from pty import spawn; spawn(["echo", "ok"])'
```

该命令应该输出 ok。如果该命令反而输出 OSError: out of pty devices，说明 PTY 在当前环境无法正常工作。

在继续构建之前，必须解决这一问题，否则需要使用 Expect 的测试套件出现大规模的测试失败，而且也可能产生其他隐蔽的问题。

对该软件包进行一些修改，以允许使用 gcc-14.1 或更新版本构建它：

```text
patch -Np1 -i ../expect-5.45.4-gcc14-1.patch
```

准备编译 Expect：

```text
./configure --prefix=/usr           \
            --with-tcl=/usr/lib     \
            --enable-shared         \
            --disable-rpath         \
            --mandir=/usr/share/man \
            --with-tclinclude=/usr/include
```

构建该软件包：

```text
time make
```

运行命令以测试编译结果：

```text
make test
```

安装该软件包：

```text
make install
ln -svf expect5.45.4/libexpect5.45.4.so /usr/lib
```

## 16. DejaGNU-1.6.3

DejaGnu 包含使用 GNU 工具运行测试套件的框架。它是用 expect 编写的，后者又使用 Tcl (工具命令语言)。

安装 DejaGNU

```text
cd /sources;tar -xf dejagnu-1.6.3.tar.gz;cd dejagnu-1.6.3
```

DejaGNU 开发者建议在专用的目录中进行构建：

```text
mkdir -v build;cd build
```

准备编译 DejaGNU：

```text
../configure --prefix=/usr
makeinfo --html --no-split -o doc/dejagnu.html ../doc/dejagnu.texi
makeinfo --plaintext       -o doc/dejagnu.txt  ../doc/dejagnu.texi
```

运行命令以测试编译结果：

```text
make check
```

安装该软件包：

```text
make install
install -v -dm755  /usr/share/doc/dejagnu-1.6.3
install -v -m644   doc/dejagnu.{html,txt} /usr/share/doc/dejagnu-1.6.3
```

## 17. Pkgconf-2.3.0

pkgconf 软件包是 pkg-config 的接替者，它包含用于在软件包安装的配置和生成阶段向构建工具传递头文件或库文件搜索路径的工具。

安装 Pkgconf

```text
cd /sources;tar -xf pkgconf-2.3.0.tar.xz;cd pkgconf-2.3.0
```

准备编译 Pkgconf：

```text
./configure --prefix=/usr              \
            --disable-static           \
            --docdir=/usr/share/doc/pkgconf-2.3.0
```

编译该软件包：

```text
time make
```

安装该软件包：

```text
make install
```

为了维持与原始的 Pkg-config 软件包的兼容性，创建两个符号链接：

```text
ln -sv pkgconf   /usr/bin/pkg-config
ln -sv pkgconf.1 /usr/share/man/man1/pkg-config.1
```

## 18. Binutils-2.44

Binutils 包含汇编器、链接器以及其他用于处理目标文件的工具。

安装 Binutils

```text
cd /sources;rm -rf binutils-2.44;tar -xf binutils-2.44.tar.xz;cd binutils-2.44
```

Binutils 文档推荐创建一个新的目录，以在其中构建 Binutils：

```text
mkdir -v build;cd build
```

准备编译 Binutils：

```text
../configure --prefix=/usr       \
             --sysconfdir=/etc   \
             --enable-ld=default \
             --enable-plugins    \
             --enable-shared     \
             --disable-werror    \
             --enable-64-bit-bfd \
             --enable-new-dtags  \
             --with-system-zlib  \
             --enable-default-hash-style=gnu
```

编译该软件包：

```text
time make tooldir=/usr
```

测试编译结果：

```text
make -k check
```

如果需要列出所有失败的测试，执行：

```text
grep '^FAIL:' $(find -name '*.log')
```

安装该软件包：

```text
make tooldir=/usr install
```

删除无用的静态库等文件：

```text
rm -rfv /usr/lib/lib{bfd,ctf,ctf-nobfd,gprofng,opcodes,sframe}.a \
        /usr/share/doc/gprofng/
```

## 19. GMP-6.3.0

GMP 软件包包含提供任意精度算术函数的数学库。

```text
cd /sources;tar -xf gmp-6.3.0.tar.xz;cd gmp-6.3.0
```

准备编译 GMP：

```text
./configure --prefix=/usr    \
            --enable-cxx     \
            --disable-static \
            --docdir=/usr/share/doc/gmp-6.3.0
```

编译该软件包，并生成 HTML 文档：

```text
make
make html
```

本节中 GMP 的测试套件是关键的。无论如何都不要跳过测试过程。

测试编译结果：

```text
make check 2>&1 | tee gmp-check-log
```

务必确认测试套件中至少 199 项测试通过。运行以下命令检验结果：

```text
awk '/# PASS:/{total+=$3} ; END{print total}' gmp-check-log
```

安装该软件包及其文档：

```text
make install
make install-html
```

## 20. MPFR-4.2.1

MPFR 软件包包含多精度数学函数。

安装 MPFR

```text
cd /sources;tar -xf mpfr-4.2.1.tar.xz;cd mpfr-4.2.1
```

准备编译 MPFR：

```text
./configure --prefix=/usr        \
            --disable-static     \
            --enable-thread-safe \
            --docdir=/usr/share/doc/mpfr-4.2.1
```

编译该软件包，并生成 HTML 文档：

```text
make
make html
```

本节中 MPFR 的测试套件被认为是非常关键的，无论如何不能跳过。

测试编译结果，并确认所有 198 项测试都能通过：

```text
make check
```

安装该软件包及其文档：

```text
make install
make install-html
```

## 21. MPC-1.3.1

MPC 软件包包含一个任意高精度，且舍入正确的复数算术库。

安装 MPC

```text
cd /sources;tar -xf mpc-1.3.1.tar.gz;cd mpc-1.3.1
```

准备编译 MPC：

```text
./configure --prefix=/usr    \
            --disable-static \
            --docdir=/usr/share/doc/mpc-1.3.1
```

编译该软件包，并生成 HTML 文档：

```text
make
make html
```

运行命令以测试编译结果：

```text
make check
```

安装该软件包及其文档：

```text
make install
make install-html
```

## 22. Attr-2.5.2

Attr 软件包包含管理文件系统对象扩展属性的工具。

安装 Attr

```text
cd /sources;tar -xf attr-2.5.2.tar.gz;cd attr-2.5.2
```

准备编译 Attr：

```text
./configure --prefix=/usr     \
            --disable-static  \
            --sysconfdir=/etc \
            --docdir=/usr/share/doc/attr-2.5.2
```

编译该软件包：

```text
time make
```

测试套件必须在支持扩展属性的文件系统，如 ext2、ext3 或 ext4 上运行。运行下列命令以测试编译结果：

```text
make check
```

安装该软件包：

```text
make install
```

## 23. Acl-2.3.2

Acl 软件包包含管理访问控制列表的工具，访问控制列表能够细致地自由定义文件和目录的访问权限。

安装 Acl

```text
cd /sources;tar -xf acl-2.3.2.tar.xz;cd acl-2.3.2
```

准备编译 Acl：

```text
./configure --prefix=/usr         \
            --disable-static      \
            --docdir=/usr/share/doc/acl-2.3.2
```

编译该软件包：

```text
make
```

测试套件必须在支持访问控制的文件系统上运行。运行下列命令以测试编译结果：

```text
make check
```

已知名为 test/cp.test 的一项测试会由于 Coreutils 的 Acl 支持尚未构建而失败。

安装该软件包：

```text
make install
```

## 24. Libcap-2.73

Libcap 软件包为 Linux 内核提供的 POSIX 1003.1e 权能字实现用户接口。这些权能字是 root 用户的最高特权分割成的一组不同权限。

安装 Libcap

```text
cd /sources;tar -xf libcap-2.73.tar.xz;cd libcap-2.73
```

防止静态库的安装：

```text
sed -i '/install -m.*STA/d' libcap/Makefile
```

编译该软件包：

```text
time make prefix=/usr lib=lib
```

运行命令以测试编译结果：

```text
make test
```

安装该软件包：

```text
make prefix=/usr lib=lib install
```

## 25. Libxcrypt-4.4.38

Libxcrypt 软件包包含用于对密码进行单向散列操作的，现代化的库。

安装 Libxcrypt

```text
cd /sources;tar -xf libxcrypt-4.4.38.tar.xz;cd libxcrypt-4.4.38
```

准备编译 Libxcrypt：

```text
./configure --prefix=/usr                \
            --enable-hashes=strong,glibc \
            --enable-obsolete-api=no     \
            --disable-static             \
            --disable-failure-tokens
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

> 注意满足 LSB 兼容性，必须使用这些函数，执行以下命令再次构建该软件包：

```text
make distclean
./configure --prefix=/usr                \
            --enable-hashes=strong,glibc \
            --enable-obsolete-api=glibc  \
            --disable-static             \
            --disable-failure-tokens
make
cp -av --remove-destination .libs/libcrypt.so.1* /usr/lib
```

## 26. Shadow-4.17.3

Shadow 软件包包含安全地处理密码的程序。

### 26.1 安装 Shadow

```text
cd /sources;tar -xf shadow-4.17.3.tar.xz;cd shadow-4.17.3
```

禁止该软件包安装 groups 程序和它的手册页，因为 Coreutils 会提供更好的版本。

```text
sed -i 's/groups$(EXEEXT) //' src/Makefile.in
find man -name Makefile.in -exec sed -i 's/groups\.1 / /'   {} \;
find man -name Makefile.in -exec sed -i 's/getspnam\.3 / /' {} \;
find man -name Makefile.in -exec sed -i 's/passwd\.5 / /'   {} \;
```

不使用默认的 crypt 加密方法，使用安全程度高很多的 YESCRYPT 算法加密密码

```text
sed -e 's:#ENCRYPT_METHOD DES:ENCRYPT_METHOD YESCRYPT:' \
    -e 's:/var/spool/mail:/var/mail:'                   \
    -e '/PATH=/{s@/sbin:@@;s@/bin:@@}'                  \
    -i etc/login.defs
```

准备编译 Shadow：

```text
touch /usr/bin/passwd
./configure --sysconfdir=/etc   \
            --disable-static    \
            --with-{b,yes}crypt \
            --without-libbsd    \
            --with-group-name-max-length=32
```

编译该软件包：

```text
time make
```

该软件包不包含测试套件。

安装该软件包：

```text
make exec_prefix=/usr install
make -C man install-man
```

### 26.2 配置 Shadow

该软件包包含用于添加、修改、删除用户和组，设定和修改它们的密码，以及进行其他管理任务的工具。

如果要对用户密码启用 Shadow 加密，执行以下命令：

```text
pwconv
```

如果要对组密码启用 Shadow 加密，执行：

```text
grpconv
```

其次，为了修改默认参数，必须创建 /etc/default/useradd 文件，并定制其内容，以满足您的特定需要。使用以下命令创建它：

```text
mkdir -p /etc/default
useradd -D --gid 999
```

如果您不希望 useradd 创建邮箱文件，执行以下命令：

```text
sed -i '/MAIL/s/yes/no/' /etc/default/useradd
```

### 26.3 设定根用户密码

为用户 root 选择一个密码，并执行以下命令设定它：

```text
passwd root
```

## 27. GCC-14.2.0

GCC 软件包包含 GNU 编译器集合，其中有 C 和 C++ 编译器。
安装 GCC

```text
cd /sources;rm -rf gcc-14.2.0;tar -xf gcc-14.2.0.tar.xz;cd gcc-14.2.0
```

在 x86_64 上构建时，修改存放 64 位库的默认路径为 “lib”:

```text
case $(uname -m) in
x86_64)
sed -e '/m64=/s/lib64/lib/' \
-i.orig gcc/config/i386/t-linux64
;;
esac
```

GCC 文档建议在一个新建的目录中构建 GCC：

```text
mkdir -v build;cd build
```

准备编译 GCC：

```text
../configure --prefix=/usr            \
             LD=ld                    \
             --enable-languages=c,c++ \
             --enable-default-pie     \
             --enable-default-ssp     \
             --enable-host-pie        \
             --disable-multilib       \
             --disable-bootstrap      \
             --disable-fixincludes    \
             --with-system-zlib
```

编译该软件包：

```text
time make
```

> 在本节中，GCC 的测试套件十分重要，但需要消耗较长的时间。

万一宿主系统的栈空间限制较为严格，我们需要手工将栈空间的硬上限设为无限大

```text
ulimit -s -H unlimited
```

现在移除或修复若干已知会失败的测试：

```text
sed -e '/cpython/d'               -i ../gcc/testsuite/gcc.dg/plugin/plugin.exp
sed -e 's/no-pic /&-no-pie /'     -i ../gcc/testsuite/gcc.target/i386/pr113689-1.c
sed -e 's/300000/(1|300000)/'     -i ../libgomp/testsuite/libgomp.c-c++-common/pr109062.c
sed -e 's/{ target nonpic } //' \
    -e '/GOTPCREL/d'              -i ../gcc/testsuite/gcc.target/i386/fentryname3.c
```

以非特权用户身份测试编译结果，但出错时继续执行其他测试：

```text
chown -R tester .
su tester -c "PATH=$PATH make -k check"
```

输入以下命令提取测试结果的摘要：

```text
../contrib/test_summary
```

安装该软件包：

```text
make install
```

GCC 构建目录目前属于用户 tester，导致安装的头文件目录 (及其内容) 具有不正确的所有权。将所有者修改为 root 用户和组：

```text
chown -v -R root:root \
/usr/lib/gcc/$(gcc -dumpmachine)/14.2.0/include{,-fixed}
```

创建一个 FHS 因 “历史原因” 要求的符号链接。

```text
ln -svr /usr/bin/cpp /usr/lib
```

许多软件包使用 cc 这一名称调用 C 编译器。
在第二遍的 GCC 中我们已经将 cc 创建为符号链接，这里将其手册页也创建为符号链接：

```text
ln -sv gcc.1 /usr/share/man/man1/cc.1
```

创建一个兼容性符号链接，以支持在构建程序时使用链接时优化 (LTO)：

```text
ln -sfv ../../libexec/gcc/$(gcc -dumpmachine)/14.2.0/liblto_plugin.so \
        /usr/lib/bfd-plugins/
```

现在最终的工具链已经就位，重要的是再次确认编译和链接像我们期望的一样正常工作。为此，进行下列完整性检查：

```text
echo 'int main(){}' > dummy.c
cc dummy.c -v -Wl,--verbose &> dummy.log
readelf -l a.out | grep ': /lib'
```

> 上述命令不应该出现错误，最后一行命令输出的结果应该 (不同平台的动态链接器名称可能不同) 是：
>
>    `[Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]`

下面确认我们在使用正确的启动文件：

```text
grep -E -o '/usr/lib.*/S?crt[1in].*succeeded' dummy.log
```

> 以上命令应该输出：
>```text
>    /usr/lib/gcc/x86_64-pc-linux-gnu/14.2.0/../../../../lib/Scrt1.o succeeded
>    /usr/lib/gcc/x86_64-pc-linux-gnu/14.2.0/../../../../lib/crti.o succeeded
>    /usr/lib/gcc/x86_64-pc-linux-gnu/14.2.0/../../../../lib/crtn.o succeeded
>```

确认编译器能正确查找头文件：

```text
grep -B4 '^ /usr/include' dummy.log
```

> 该命令应当输出：
>```text
>    #include <...> search starts here:
>    /usr/lib/gcc/x86_64-pc-linux-gnu/14.2.0/include
>    /usr/local/include
>    /usr/lib/gcc/x86_64-pc-linux-gnu/14.2.0/include-fixed
>    /usr/include
>```

下一步确认新的链接器使用了正确的搜索路径：

```text
grep 'SEARCH.*/usr/lib' dummy.log |sed 's|; |\n|g'
```

> 那些包含 '-linux-gnu' 的路径应该忽略，除此之外，以上命令应该输出：
>```text
>    SEARCH_DIR("/usr/x86_64-pc-linux-gnu/lib64")
>    SEARCH_DIR("/usr/local/lib64")
>    SEARCH_DIR("/lib64")
>    SEARCH_DIR("/usr/lib64")
>    SEARCH_DIR("/usr/x86_64-pc-linux-gnu/lib")
>    SEARCH_DIR("/usr/local/lib")
>    SEARCH_DIR("/lib")
>    SEARCH_DIR("/usr/lib");
>```

之后确认我们使用了正确的 libc：

```text
grep "/lib.*/libc.so.6 " dummy.log
```

> 以上命令应该输出：
>
>    attempt to open /usr/lib/libc.so.6 succeeded

确认 GCC 使用了正确的动态链接器：

```text
grep found dummy.log
```

> 以上命令应该输出 (不同平台的动态链接器名称可能不同):
>
>    found ld-linux-x86-64.so.2 at /usr/lib/ld-linux-x86-64.so.2

在确认一切工作良好后，删除测试文件：

```text
rm -v dummy.c a.out dummy.log
```

最后移动一个位置不正确的文件：

```text
mkdir -pv /usr/share/gdb/auto-load/usr/lib
mv -v /usr/lib/*gdb.py /usr/share/gdb/auto-load/usr/lib
```
