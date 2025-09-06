# LFS 安装基本系统软件 Part2

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
make test
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

## 47. Elfutils-0.192 中的 Libelf

Libelf 是一个处理 ELF (可执行和可链接格式) 文件的库。

Libelf 是 elfutils-0.192 软件包的一部分。请使用 elfutils-0.192.tar.bz2 作为源代码包。

```text
cd /sources;tar -xf elfutils-0.192.tar.bz2;cd elfutils-0.192
```

准备编译 Libelf：

```text
./configure --prefix=/usr                \
            --disable-debuginfod         \
            --enable-libdebuginfod=dummy
```

编译该软件包：

```text
time make
```

运行命令以测试编译结果：

```text
make check
```

只安装 Libelf：

```text
make -C libelf install
install -vm644 config/libelf.pc /usr/lib/pkgconfig
rm /usr/lib/libelf.a
```

## 48. Libffi-3.4.7

Libffi 库提供一个可移植的高级编程接口，用于处理不同调用惯例。这允许程序在运行时调用任何给定了调用接口的函数。

FFI 是 Foreign Function Interface (跨语言函数接口) 的缩写。
FFI 允许使用某种编程语言编写的程序调用其他语言编写的程序。

特别地，Libffi 为 Perl 或 Python 等解释器提供使用 C 或 C++ 编写的共享库中子程序的能力。

```text
cd /sources;tar -xf libffi-3.4.7.tar.gz;cd libffi-3.4.7
```

准备编译 Libffi：

```text
./configure --prefix=/usr          \
            --disable-static       \
            --with-gcc-arch=native
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

## 49. Python-3.13.2

Python 3 软件包包含 Python 开发环境。

它被用于面向对象编程，编写脚本，为大型程序建立原型，或者开发完整的应用。

Python 是一种解释性的计算机语言。

```text
cd /sources;rm -rf Python-3.13.2;tar -xf Python-3.13.2.tar.xz;cd Python-3.13.2
```

准备编译 Python：

```text
./configure --prefix=/usr        \
            --enable-shared      \
            --with-system-expat  \
            --enable-optimizations
```

编译该软件包：

```text
time make
```

运行测试套件，但是将每个单项测试的最长运行时间限制为 2 分钟：

```text
make test TESTOPTS="--timeout 120"
```

安装该软件包：

```text
make install
```

应该忽略关于 pip3 新版本的警告。如果您不想看到这些警告，可以执行以下命令，创建配置文件，以禁止这些警告：

```text
cat > /etc/pip.conf << EOF
[global]
root-user-action = ignore
disable-pip-version-check = true
EOF
```

如果需要的话，安装预先格式化的文档：

```text
install -v -dm755 /usr/share/doc/python-3.13.2/html

tar --strip-components=1  \
    --no-same-owner       \
    --no-same-permissions \
    -C /usr/share/doc/python-3.13.2/html \
    -xvf ../python-3.13.2-docs-html.tar.bz2
```

## 50. Flit-Core-3.11.0

Flit-core 是 Flit (一个用于简单的 Python 模块的打包工具) 中用于为发行版进行构建的组件。

```text
cd /sources;tar -xf flit_core-3.11.0.tar.gz;cd flit_core-3.11.0
```

构建该软件包：

```text
pip3 wheel -w dist --no-cache-dir --no-build-isolation --no-deps $PWD
```

安装该软件包：

```text
pip3 install --no-index --find-links dist flit_core
```
