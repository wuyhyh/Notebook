# LFS 安装基本系统软件 Part2

## 28. Ncurses-6.5

Ncurses 软件包包含使用时不需考虑终端特性的字符屏幕处理函数库。

安装 Ncurses

```text
cd /sources;rm -rf ncurses-6.5;tar -xf ncurses-6.5.tar.gz;cd ncurses-6.5
```

准备编译 Ncurses：

```text
./configure --prefix=/usr           \
            --mandir=/usr/share/man \
            --with-shared           \
            --without-debug         \
            --without-normal        \
            --with-cxx-shared       \
            --enable-pc-files       \
            --with-pkg-config-libdir=/usr/lib/pkgconfig
```

编译该软件包：

```text
time make
```

需要使用 DESTDIR 进行安装，并正确地使用 install 命令安装库文件：

```text
make DESTDIR=$PWD/dest install
install -vm755 dest/usr/lib/libncursesw.so.6.5 /usr/lib
rm -v  dest/usr/lib/libncursesw.so.6.5
sed -e 's/^#if.*XOPEN.*$/#if 1/' \
    -i dest/usr/include/curses.h
cp -av dest/* /
```

许多程序仍然希望链接器能够找到非宽字符版本的 Ncurses 库。

```text
for lib in ncurses form panel menu ; do
ln -sfv lib${lib}w.so /usr/lib/lib${lib}.so
ln -sfv ${lib}w.pc    /usr/lib/pkgconfig/${lib}.pc
done
```

最后，确保那些在构建时寻找 -lcurses 的老式程序仍然能够构建：

```text
ln -sfv libncursesw.so /usr/lib/libcurses.so
```

如果需要的话，安装 Ncurses 文档：

```text
cp -v -R doc -T /usr/share/doc/ncurses-6.5
```

满足 LSB 兼容性，必须安装这样的库，执行以下命令再次构建该软件包：

```text
make distclean
./configure --prefix=/usr    \
            --with-shared    \
            --without-normal \
            --without-debug  \
            --without-cxx-binding \
            --with-abi-version=5
make sources libs
cp -av lib/lib*.so.5* /usr/lib
```

## 29. Sed-4.9

Sed 软件包包含一个流编辑器。

安装 Sed

```text
cd /sources;rm -rf sed-4.9;tar -xf sed-4.9.tar.xz;cd sed-4.9
```

准备编译 Sed：

```text
./configure --prefix=/usr
```

编译该软件包，并生成 HTML 文档：

```text
make
make html
```

运行命令以测试编译结果：

```text
chown -R tester .
su tester -c "PATH=$PATH make check"
```

安装该软件包及其文档：

```text
make install
install -d -m755           /usr/share/doc/sed-4.9
install -m644 doc/sed.html /usr/share/doc/sed-4.9
```

## 30. Psmisc-23.7

Psmisc 软件包包含显示正在运行的进程信息的程序。

安装 Psmisc

```text
cd /sources;tar -xf psmisc-23.7.tar.xz;cd psmisc-23.7
```

准备编译 Psmisc：

```text
./configure --prefix=/usr
```

编译该软件包：

```text
time make
```

如果要运行测试套件，执行命令：

```text
make check
```

安装该软件包：

```text
make install
```

## 31. Gettext-0.24

Gettext 软件包包含国际化和本地化工具，它们允许程序在编译时加入 NLS (本地语言支持) 功能，使它们能够以用户的本地语言输出消息。

安装 Gettext

```text
cd /sources;rm -rf gettext-0.24;tar -xf gettext-0.24.tar.xz;cd gettext-0.24
```

准备编译 Gettext：

```text
./configure --prefix=/usr    \
            --disable-static \
            --docdir=/usr/share/doc/gettext-0.24
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
chmod -v 0755 /usr/lib/preloadable_libintl.so
```

## 32. Bison-3.8.2

Bison 软件包包含语法分析器生成器。

安装 Bison

```text
cd /sources;rm -rf bison-3.8.2;tar -xf bison-3.8.2.tar.xz;cd bison-3.8.2
```

准备编译 Bison：

```text
./configure --prefix=/usr --docdir=/usr/share/doc/bison-3.8.2
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

## 33. Grep-3.11

Grep 软件包包含在文件内容中进行搜索的程序。

安装 Grep

```text
cd /sources;rm -rf grep-3.11;tar -xf grep-3.11.tar.xz;cd grep-3.11
```

首先，移除使用 egrep 和 fgrep 时的警告，它会导致一些软件包测试失败：

```text
sed -i "s/echo/#echo/" src/egrep.sh
```

准备编译 Grep：

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

## 34. Bash-5.2.37

Bash 软件包包含 Bourne-Again Shell。

安装 Bash

```text
cd /sources;rm -rf bash-5.2.37;tar -xf bash-5.2.37.tar.gz;cd bash-5.2.37
```

准备编译 Bash：

```text
./configure --prefix=/usr             \
            --without-bash-malloc     \
            --with-installed-readline \
            --docdir=/usr/share/doc/bash-5.2.37
```

编译该软件包：

```text
time make
```

为了准备进行测试，确保 tester 用户可以写入源代码目录：

```text
chown -R tester .
```

该软件包的测试套件被设计为以非 root 用户身份运行，且该用户必须是标准输入所连接的终端的所有者。
为了满足这一条件，使用 Expect 生成一个新的伪终端，并以 tester 用户身份运行测试：

```text
su -s /usr/bin/expect tester << "EOF"
set timeout -1
spawn make tests
expect eof
lassign [wait] _ _ _ value
exit $value
EOF
```

测试套件使用 diff 检测测试脚本输出和预期是否存在不同

安装该软件包：

```text
make install
```

执行新编译的 bash 程序 (替换当前正在执行的版本)：

```text
exec /usr/bin/bash --login
```

## 35. Libtool-2.5.4

Libtool 软件包包含 GNU 通用库支持脚本。它提供一致、可移植的接口，以简化共享库的使用。

安装 Libtool

```text
cd /sources;tar -xf libtool-2.5.4.tar.xz;cd libtool-2.5.4
```

准备编译 Libtool：

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

删除无用的静态库：

```text
rm -fv /usr/lib/libltdl.a
```

## 36. GDBM-1.24

GDBM 软件包包含 GNU 数据库管理器。

安装 GDBM

```text
cd /sources;tar -xf gdbm-1.24.tar.gz;cd gdbm-1.24
```

准备编译 GDBM：

```text
./configure --prefix=/usr    \
            --disable-static \
            --enable-libgdbm-compat
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

## 37. Gperf-3.1

Gperf 根据一组键值，生成完美散列函数。

安装 Gperf

```text
cd /sources;tar -xf gperf-3.1.tar.gz;cd gperf-3.1
```

准备编译 Gperf：

```text
./configure --prefix=/usr --docdir=/usr/share/doc/gperf-3.1
```

编译该软件包：

```text
time make
```

已知同时执行多个测试 (-j 选项的值大于 1) 会导致测试失败。执行以下命令测试编译结果：

```text
make -j1 check
```

安装该软件包：

```text
make install
```

## 38. Expat-2.6.4

Expat 软件包包含用于解析 XML 文件的面向流的 C 语言库。

安装 Expat

```text
cd /sources;tar -xf expat-2.6.4.tar.xz;cd expat-2.6.4
```

准备编译 Expat：

```text
./configure --prefix=/usr    \
            --disable-static \
            --docdir=/usr/share/doc/expat-2.6.4
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

如果需要，安装该软件包的文档：

```text
install -v -m644 doc/*.{html,css} /usr/share/doc/expat-2.6.4
```

## 39. Inetutils-2.6

Inetutils 软件包包含基本网络程序。

```text
cd /sources;tar -xf inetutils-2.6.tar.xz;cd inetutils-2.6
```

首先，使得该软件包能够用 gcc-14.1 或更新版本构建：

````text
sed -i 's/def HAVE_TERMCAP_TGETENT/ 1/' telnet/telnet.c
````

准备编译 Inetutils：

```text
./configure --prefix=/usr        \
            --bindir=/usr/bin    \
            --localstatedir=/var \
            --disable-logger     \
            --disable-whois      \
            --disable-rcp        \
            --disable-rexec      \
            --disable-rlogin     \
            --disable-rsh        \
            --disable-servers
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

将一个程序移动到正确的位置：

```text
mv -v /usr/{,s}bin/ifconfig
```

## 40. Less-668

Less 软件包包含一个文本文件查看器。

```text
cd /sources;tar -xf less-668.tar.gz;cd less-668
```

准备编译 Less：

```text
./configure --prefix=/usr --sysconfdir=/etc
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

## 41. Perl-5.40.1

Perl 软件包包含实用报表提取语言。

```text
cd /sources;rm -rf perl-5.40.1;tar -xf perl-5.40.1.tar.xz;cd perl-5.40.1
```

执行以下命令，使得 Perl 使用已经安装到系统上的库：

```text
export BUILD_ZLIB=False
export BUILD_BZIP2=0
```

使用下面给出的命令，以使用 Perl 自动检测的默认值

```text
sh Configure -des                                          \
             -D prefix=/usr                                \
             -D vendorprefix=/usr                          \
             -D privlib=/usr/lib/perl5/5.40/core_perl      \
             -D archlib=/usr/lib/perl5/5.40/core_perl      \
             -D sitelib=/usr/lib/perl5/5.40/site_perl      \
             -D sitearch=/usr/lib/perl5/5.40/site_perl     \
             -D vendorlib=/usr/lib/perl5/5.40/vendor_perl  \
             -D vendorarch=/usr/lib/perl5/5.40/vendor_perl \
             -D man1dir=/usr/share/man/man1                \
             -D man3dir=/usr/share/man/man3                \
             -D pager="/usr/bin/less -isR"                 \
             -D useshrplib                                 \
             -D usethreads
```

编译该软件包：

```text
time make
```

运行命令以测试编译结果：

```text
TEST_JOBS=$(nproc) make test_harness
```

安装该软件包，并清理环境变量：

```text
make install
unset BUILD_ZLIB BUILD_BZIP2
```

## 42. XML::Parser-2.47

XML::Parser 模块是 James Clark 的 XML 解析器 Expat 的 Perl 接口。

```text
cd /sources;tar -xf XML-Parser-2.47.tar.gz;cd XML-Parser-2.47
```

准备编译 XML::Parser：

```text
perl Makefile.PL
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

## 43. Intltool-0.51.0

Intltool 是一个从源代码文件中提取可翻译字符串的国际化工具。

```text
cd /sources;tar -xf intltool-0.51.0.tar.gz;cd intltool-0.51.0
```

首先修复由 perl-5.22 及更新版本导致的警告：

```text
sed -i 's:\\\${:\\\$\\{:' intltool-update.in
```

准备编译 Intltool：

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
install -v -Dm644 doc/I18N-HOWTO /usr/share/doc/intltool-0.51.0/I18N-HOWTO
```

## 44. Autoconf-2.72

Autoconf 软件包包含生成能自动配置软件包的 shell 脚本的程序。

```text
cd /sources;tar -xf autoconf-2.72.tar.xz;cd autoconf-2.72
```

准备编译 Intltool：

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

## 45. Automake-1.17

Automake 软件包包含自动生成 Makefile，以便和 Autoconf 一同使用的程序。

```text
cd /sources;tar -xf automake-1.17.tar.xz;cd automake-1.17
```

准备编译 Automake：

```text
./configure --prefix=/usr --docdir=/usr/share/doc/automake-1.17
```

编译该软件包：

```text
time make
```

输入以下命令测试编译结果：

```text
make -j$(($(nproc)>4?$(nproc):4)) check
```

安装该软件包：

```text
make install
```

## 46. OpenSSL-3.4.1

OpenSSL 软件包包含密码学相关的管理工具和库。

它们被用于向其他软件包提供密码学功能，例如 OpenSSH，电子邮件程序和 Web 浏览器 (以访问 HTTPS 站点)。

```text
cd /sources;tar -xf openssl-3.4.1.tar.gz;cd openssl-3.4.1
```

准备编译 OpenSSL：

```text
./config --prefix=/usr         \
         --openssldir=/etc/ssl \
         --libdir=lib          \
         shared                \
         zlib-dynamic
```

编译该软件包：

```text
time make
```

运行命令以测试编译结果：

```text
HARNESS_JOBS=$(nproc) make test
```

安装该软件包：

```text
sed -i '/INSTALL_LIBS/s/libcrypto.a libssl.a//' Makefile
make MANSUFFIX=ssl install
```

将版本号添加到文档目录名，以和其他软件包保持一致：

```text
mv -v /usr/share/doc/openssl /usr/share/doc/openssl-3.4.1
```

如果需要的话，安装一些额外的文档：

```text
cp -vfr doc/* /usr/share/doc/openssl-3.4.1
```

## 47. 
