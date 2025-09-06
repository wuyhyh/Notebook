# LFS 安装基本系统软件 Part3

## 51. Wheel-0.45.1

Wheel 是 Python wheel 软件包标准格式的参考实现。

```text
cd /sources;tar -xf wheel-0.45.1.tar.gz;cd wheel-0.45.1
```

执行以下命令编译 Wheel：

```text
pip3 wheel -w dist --no-cache-dir --no-build-isolation --no-deps $PWD
```

使用以下命令安装 Wheel：

```text
pip3 install --no-index --find-links dist wheel
```

## 52. Setuptools-75.8.1

Setuptools 是一个用于下载、构建、安装、升级，以及卸载 Python 软件包的工具。

```text
cd /sources;tar -xf setuptools-75.8.1.tar.gz;cd setuptools-75.8.1
```

构建该软件包：

```text
pip3 wheel -w dist --no-cache-dir --no-build-isolation --no-deps $PWD
```

安装该软件包：

```text
pip3 install --no-index --find-links dist setuptools
```

## 53. Ninja-1.12.1

Ninja 是一个注重速度的小型构建系统。

```text
cd /sources;tar -xf ninja-1.12.1.tar.gz;cd ninja-1.12.1
```

可通过一个环境变量 NINJAJOBS 限制并行进程数量。例如设置：

```text
export NINJAJOBS=4
```

会限制 ninja 使用 4 个并行进程。

如果希望 ninja 能够识别环境变量 NINJAJOBS，使用流编辑器，添加这一功能：

```text
sed -i '/int Guess/a \
int   j = 0;\
char* jobs = getenv( "NINJAJOBS" );\
if ( jobs != NULL ) j = atoi( jobs );\
if ( j > 0 ) return j;\
' src/ninja.cc
```

构建 Ninja：

```text
python3 configure.py --bootstrap --verbose
```

测试套件无法在 chroot 环境中运行。它需要 cmake。
不过，重新构建该软件包本身 (由 --bootstrap 选项要求) 已经测试了它的基本功能。

安装该软件包：

```text
install -vm755 ninja /usr/bin/
install -vDm644 misc/bash-completion /usr/share/bash-completion/completions/ninja
install -vDm644 misc/zsh-completion  /usr/share/zsh/site-functions/_ninja
```

## 54. Meson-1.7.0

Meson 是一个开放源代码构建系统，它的设计保证了非常快的执行速度，和尽可能高的用户友好性。

```text
cd /sources;tar -xf meson-1.7.0.tar.gz;cd meson-1.7.0
```

执行以下命令编译 Meson：

```text
pip3 wheel -w dist --no-cache-dir --no-build-isolation --no-deps $PWD
```

测试套件需要一些超过 LFS 覆盖范围的软件包。

安装该软件包：

```text
pip3 install --no-index --find-links dist meson
install -vDm644 data/shell-completions/bash/meson /usr/share/bash-completion/completions/meson
install -vDm644 data/shell-completions/zsh/_meson /usr/share/zsh/site-functions/_meson
```

## 55. Kmod-34

Kmod 软件包包含用于加载内核模块的库和工具。

```text
cd /sources;tar -xf kmod-34.tar.xz;cd kmod-34
```

准备编译 Kmod：

```text
mkdir -p build
cd       build

meson setup --prefix=/usr ..    \
            --sbindir=/usr/sbin \
            --buildtype=release \
            -D manpages=false
```

编译该软件包：

```text
ninja
```

该软件包的测试套件需要内核的原始头文件 (不是之前安装的 “净化的” 内核头文件)，原始头文件超出了 LFS 的范畴。

现在安装该软件包：

```text
ninja install
```

## 56. Coreutils-9.6

Coreutils 软件包包含各种操作系统都需要提供的基本工具程序。

```text
cd /sources;rm -rf coreutils-9.6;tar -xf coreutils-9.6.tar.xz;cd coreutils-9.6
```

应用一个补丁，以解决 Coreutils 不满足该要求的问题，并修复其他一些国际化相关的 bug：

```text
patch -Np1 -i ../coreutils-9.6-i18n-1.patch
```

现在准备编译 Coreutils：

```text
autoreconf -fv
automake -af
FORCE_UNSAFE_CONFIGURE=1 ./configure \
            --prefix=/usr            \
            --enable-no-install-program=kill,uptime
```

编译该软件包：

```text
time make
```

现在测试套件已经可以运行了。首先运行那些设计为由 root 用户运行的测试：

```text
make NON_ROOT_USERNAME=tester check-root
```

之后我们要以 tester 用户身份运行其余测试。然而，某些测试要求测试用户属于至少一个组。为了不跳过这些测试，我们添加一个临时组，并使得
tester 用户成为它的成员：

```text
groupadd -g 102 dummy -U tester
```

修正访问权限，使得非 root 用户可以编译和运行测试：

```text
chown -R tester .
```

现在运行测试 (使用 /dev/null 作为标准输入，否则在图形终端，SSH 会话，或者 GNU Screen 构建 LFS 时，由于标准输入连接到了宿主发行版的
PTY，而该 PTY 的设备节点无法在 LFS chroot 环境中访问，两项测试无法正常工作)：

```text
su tester -c "PATH=$PATH make -k RUN_EXPENSIVE_TESTS=yes check" \
< /dev/null
```

删除临时组：

```text
groupdel dummy
```

安装该软件包：

```text
make install
```

将程序移动到 FHS 要求的位置：

```text
mv -v /usr/bin/chroot /usr/sbin
mv -v /usr/share/man/man1/chroot.1 /usr/share/man/man8/chroot.8
sed -i 's/"1"/"8"/' /usr/share/man/man8/chroot.8
```

## 57. Check-0.15.2

Check 是一个 C 语言单元测试框架。

```text
cd /sources;tar -xf check-0.15.2.tar.gz;cd check-0.15.2
```

准备编译 Check：

```text
./configure --prefix=/usr --disable-static
```

构建该软件包：

```text
time make
```

现在编译已经完成，执行以下命令执行 Check 测试套件：

```text
make check
```

安装该软件包：

```text
make docdir=/usr/share/doc/check-0.15.2 install
```

## 58. Diffutils-3.11

Diffutils 软件包包含显示文件或目录之间差异的程序。

```text
cd /sources;rm -rf diffutils-3.11;tar -xf diffutils-3.11.tar.xz;cd diffutils-3.11
```

准备编译 Diffutils：

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

## 59. Gawk-5.3.1

Gawk 软件包包含操作文本文件的程序。

安装 Gawk

```text
cd /sources;rm -rf gawk-5.3.1;tar -xf gawk-5.3.1.tar.xz;cd gawk-5.3.1
```

首先，确保不安装某些不需要的文件：

```text
sed -i 's/extras//' Makefile.in
```

准备编译 Gawk：

```text
./configure --prefix=/usr
```

编译该软件包：

```text
time make
```

运行命令以测试编译结果：

```text
chown -R tester .
su tester -c "PATH=$PATH make check"
```

安装该软件包：

```text
rm -f /usr/bin/gawk-5.3.1
make install
```

安装过程已经将 awk 创建为符号链接，将其手册页也创建为符号链接：

```text
ln -sv gawk.1 /usr/share/man/man1/awk.1
```

如果需要，安装该软件包的文档：

```text
install -vDm644 doc/{awkforai.txt,*.{eps,pdf,jpg}} -t /usr/share/doc/gawk-5.3.1
```

## 60. Findutils-4.10.0

Findutils 软件包包含用于查找文件的程序。

这些程序能直接搜索目录树中的所有文件，也可以创建、维护和搜索文件数据库 (一般比递归搜索快，但在数据库最近没有更新时不可靠)。

Findutils 还提供了 xargs 程序，它能够对一次搜索列出的所有文件执行给定的命令。

```text
cd /sources;rm -rf findutils-4.10.0;tar -xf findutils-4.10.0.tar.xz;cd findutils-4.10.0
```

准备编译 Findutils：

```text
./configure --prefix=/usr --localstatedir=/var/lib/locate
```

编译该软件包：

```text
time make
```

运行命令以测试编译结果：

```text
chown -R tester .
su tester -c "PATH=$PATH make check"
```

安装该软件包：

```text
make install
```

## 61. Groff-1.23.0

Groff 软件包包含处理和格式化文本和图像的程序。

```text
cd /sources;tar -xf groff-1.23.0.tar.gz;cd groff-1.23.0
```

准备编译 Groff：

```text
PAGE=A4 ./configure --prefix=/usr
```

构建该软件包：

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

## 62. GRUB-2.12

GRUB 软件包包含 “大统一” (GRand Unified) 启动引导器。

```text
cd /sources;tar -xf grub-2.12.tar.xz;cd grub-2.12
```

> 警告：移除所有可能影响构建的环境变量：
> ```text
> unset {C,CPP,CXX,LD}FLAGS
> ```

补充源码包发布时缺失的一个文件：

```text
echo depends bli part_gpt > grub-core/extra_deps.lst
```

准备编译 GRUB：

```text
./configure --prefix=/usr          \
            --sysconfdir=/etc      \
            --disable-efiemu       \
            --disable-werror
```

编译该软件包：

```text
time make
```

不推荐运行该软件包的测试套件。

安装该软件包，并将 Bash 自动补全支持文件移动到 Bash 自动补全维护者建议的位置：

```text
make install
mv -v /etc/bash_completion.d/grub /usr/share/bash-completion/completions
```

## 63. Gzip-1.13

Gzip 软件包包含压缩和解压缩文件的程序。

```text
cd /sources;rm -rf gzip-1.13;tar -xf gzip-1.13.tar.xz;cd gzip-1.13
```

准备编译 Gzip：

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

## 64. IPRoute2-6.13.0

IPRoute2 软件包包含基于 IPv4 的基本和高级网络程序。

```text
cd /sources;tar -xf iproute2-6.13.0.tar.xz;cd iproute2-6.13.0
```

该软件包中的 arpd 程序依赖于 LFS 不安装的 Berkeley DB，因此不会被构建。
然而，用于 arpd 的一个目录和它的手册页仍会被安装。
运行以下命令以防止它们的安装。

```text
sed -i /ARPD/d Makefile
rm -fv man/man8/arpd.8
```

编译该软件包：

```text
time make NETNS_RUN_DIR=/run/netns
```

该软件包没有能够工作的测试套件。

安装该软件包：

```text
make SBINDIR=/usr/sbin install
```

如果需要，安装该软件包的文档：

```text
install -vDm644 COPYING README* -t /usr/share/doc/iproute2-6.13.0
```

## 65. Kbd-2.7.1

Kbd 软件包包含按键表文件、控制台字体和键盘工具。

```text
cd /sources;tar -xf kbd-2.7.1.tar.xz;cd kbd-2.7.1
```

退格和删除键的行为在 Kbd 软件包的不同按键映射中不一致。
以下补丁修复 i386 按键映射中的这个问题：

```text
patch -Np1 -i ../kbd-2.7.1-backspace-1.patch
```

在应用补丁后，退格键生成编码为 127 的字符，删除键生成广为人知的 escape 序列。

删除多余的 resizecons 程序 (它需要已经不存在的 svgalib 提供视频模式文件 —— 一般使用 setfont 即可调整控制台大小) 及其手册页。

```text
sed -i '/RESIZECONS_PROGS=/s/yes/no/' configure
sed -i 's/resizecons.8 //' docs/man/man8/Makefile.in
```

准备编译 Kbd：

```text
./configure --prefix=/usr --disable-vlock
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
cp -R -v docs/doc -T /usr/share/doc/kbd-2.7.1
```

## 66. Libpipeline-1.5.8

Libpipeline 软件包包含用于灵活、方便地处理子进程流水线的库。

```text
cd /sources;tar -xf libpipeline-1.5.8.tar.gz;cd libpipeline-1.5.8
```

准备编译 Libpipeline：

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

## 67. Make-4.4.1

Make 软件包包含一个程序，用于控制从软件包源代码生成可执行文件和其他非源代码文件的过程。

```text
cd /sources;rm -rf make-4.4.1;tar -xf make-4.4.1.tar.gz;cd make-4.4.1
```

准备编译 Make：

```text
./configure --prefix=/usr
```

编译该软件包：

```text
time make
```

运行命令以测试编译结果：

```text
chown -R tester .
su tester -c "PATH=$PATH make check"
```

安装该软件包：

```text
make install
```

## 68. Patch-2.7.6

Patch 软件包包含通过应用 “补丁” 文件，修改或创建文件的程序，补丁文件通常是 diff 程序创建的。

```text
cd /sources;rm -rf patch-2.7.6;tar -xf patch-2.7.6.tar.xz;cd patch-2.7.6
```

准备编译 Patch：

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

## 69. Tar-1.35

Tar 软件包提供创建 tar 归档文件，以及对归档文件进行其他操作的功能。

Tar 可以对已经创建的归档文件进行提取文件，存储新文件，更新文件，或者列出文件等操作。

```text
cd /sources;rm -rf tar-1.35;tar -xf tar-1.35.tar.xz;cd tar-1.35
```

准备编译 Tar：

```text
FORCE_UNSAFE_CONFIGURE=1  \
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

一项名为 capabilities: binary store/restore 的测试在运行时会失败，这是由于 LFS 没有 selinux 功能，但如果宿主系统的内核在构建
LFS 使用的文件系统上不支持扩展属性或安全标记，该测试会被跳过。

安装该软件包：

```text
make install
make -C doc install-html docdir=/usr/share/doc/tar-1.35
```

## 70. Texinfo-7.2

Texinfo 软件包包含阅读、编写和转换 info 页面的程序。

```text
cd /sources;rm -rf texinfo-7.2;tar -xf texinfo-7.2.tar.xz;cd texinfo-7.2
```

准备编译 Texinfo：

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

可选地，安装属于 TeX 环境的组件：

```text
make TEXMF=/usr/share/texmf install-tex
```

需要重新创建 /usr/share/info/dir 文件，可以运行以下命令完成这一工作：

```text
pushd /usr/share/info
rm -v dir
for f in *
do install-info $f dir 2>/dev/null
done
popd
```

## 71. Vim-9.1.1166

Vim 软件包包含强大的文本编辑器。

```text
cd /sources;tar -xf vim-9.1.1166.tar.gz;cd vim-9.1.1166
```

### 71.1 安装 vim

修改 vimrc 配置文件的默认位置为 /etc：

```text
echo '#define SYS_VIMRC_FILE "/etc/vimrc"' >> src/feature.h
```

准备编译 Vim：

```text
./configure --prefix=/usr
```

编译该软件包：

```text
time make
```

为了准备运行测试套件，需要使得 tester 用户拥有写入源代码目录树的权限，并排除一个含有需要 curl 或 wget 的测试的文件：

```text
chown -R tester .
sed '/test_plugin_glvs/d' -i src/testdir/Make_all.mak
```

现在，以 tester 用户身份运行测试：

```text
su tester -c "TERM=xterm-256color LANG=en_US.UTF-8 make -j1 test" \
   &> vim-test.log
```

安装该软件包：

```text
make install
```

为了在用户习惯性地输入 vi 时能够执行 vim，为二进制程序和各种语言的手册页创建符号链接：

```text
ln -sv vim /usr/bin/vi
for L in  /usr/share/man/{,*/}man1/vim.1; do
ln -sv vim.1 $(dirname $L)/vi.1
done
```

下面创建符号链接，使得可以通过 /usr/share/doc/vim-9.1.1166 访问文档，这个路径与其他软件包的文档位置格式一致：

```text
ln -sv ../vim/vim91/doc /usr/share/doc/vim-9.1.1166
```

### 71.2 配置 vim

执行以下命令创建默认 vim 配置文件：

```text
cat > /etc/vimrc << "EOF"
" Begin /etc/vimrc

" Ensure defaults are set before customizing settings, not after
source $VIMRUNTIME/defaults.vim
let skip_defaults_vim=1

set nocompatible
set backspace=2
set mouse=
syntax on
if (&term == "xterm") || (&term == "putty")
  set background=dark
endif

" End /etc/vimrc
EOF
```

## 72. MarkupSafe-3.0.2

MarkupSafe 是一个为 XML/HTML/XHTML 标记语言实现字符串安全处理的 Python 模块。

```text
cd /sources;tar -xf markupsafe-3.0.2.tar.gz;cd markupsafe-3.0.2
```

输入以下命令，编译 MarkupSafe：

```text
pip3 wheel -w dist --no-cache-dir --no-build-isolation --no-deps $PWD
```

该软件包不包含测试套件。

安装该软件包：

```text
pip3 install --no-index --find-links dist Markupsafe
```

## 73. Jinja2-3.1.5

Jinja2 是一个实现了简单的，Python 风格的模板语言的 Python 模块。

```text
cd /sources;tar -xf jinja2-3.1.5.tar.gz;cd jinja2-3.1.5
```

构建该软件包：

```text
pip3 wheel -w dist --no-cache-dir --no-build-isolation --no-deps $PWD
```

安装该软件包：

```text
pip3 install --no-index --find-links dist Jinja2
```

## 74. Systemd-257.3

Systemd 软件包包含控制系统引导、运行和关闭的程序。

```text
cd /sources;tar -xf systemd-257.3.tar.gz;cd systemd-257.3
```

从默认的 udev 规则中删除不必要的组 render 和 sgx：

```text
sed -e 's/GROUP="render"/GROUP="video"/' \
    -e 's/GROUP="sgx", //'               \
    -i rules.d/50-udev-default.rules.in
```

准备安装 systemd：

```text
mkdir -p build
cd       build

meson setup ..                \
      --prefix=/usr           \
      --buildtype=release     \
      -D default-dnssec=no    \
      -D firstboot=false      \
      -D install-tests=false  \
      -D ldconfig=false       \
      -D sysusers=false       \
      -D rpmmacrosdir=no      \
      -D homed=disabled       \
      -D userdb=false         \
      -D man=disabled         \
      -D mode=release         \
      -D pamconfdir=no        \
      -D dev-kvm-mode=0660    \
      -D nobody-group=nogroup \
      -D sysupdate=disabled   \
      -D ukify=disabled       \
      -D docdir=/usr/share/doc/systemd-257.3
```

编译该软件包：

```text
ninja
```

一些测试需要包含基本信息的 /etc/os-release 文件。如果需要测试结果，运行：

```text
echo 'NAME="Linux From Scratch"' > /etc/os-release
ninja test
```

安装该软件包：

```text
ninja install
```

安装手册页：

```text
tar -xf ../../systemd-man-pages-257.3.tar.xz \
    --no-same-owner --strip-components=1   \
    -C /usr/share/man
```

创建 /etc/machine-id 文件，systemd-journald 需要它：

```text
systemd-machine-id-setup
```

设定启动目标单元的基本结构：

```text
systemctl preset-all
```

## 75. D-Bus-1.16.0

D-bus 是一个消息总线系统，即应用程序之间互相通信的一种简单方式。

D-Bus 提供一个系统守护进程 (负责 “添加了新硬件” 或 “打印队列发生改变” 等事件)，并对每个用户登录会话提供一个守护进程 (
负责一般用户程序的进程间通信)。

另外，消息总线被构建在一个通用的一对一消息传递网络上，它可以被任意两个程序用于直接通信 (不需通过消息总线守护进程)。

```text
cd /sources;tar -xf dbus-1.16.0.tar.xz;cd dbus-1.16.0
```

准备编译 D-Bus：

```text
mkdir build;cd build
meson setup --prefix=/usr --buildtype=release --wrap-mode=nofallback ..
```

编译该软件包：

```text
ninja
```

运行命令以测试编译结果：

```text
ninja test
```

许多测试被禁用，因为它们需要 LFS 不包含的软件包。

安装该软件包：

```text
ninja install
```

创建符号链接，使 D-Bus 和 systemd 使用同一个 machine-id 文件：

```text
ln -sfv /etc/machine-id /var/lib/dbus
```

## 76. Man-DB-2.13.0

Man-DB 软件包包含查找和阅读手册页的程序。

```text
cd /sources;rm -rf man-db-2.13.0;tar -xf man-db-2.13.0.tar.xz;cd man-db-2.13.0
```

准备编译 Man-DB：

```text
./configure --prefix=/usr                         \
            --docdir=/usr/share/doc/man-db-2.13.0 \
            --sysconfdir=/etc                     \
            --disable-setuid                      \
            --enable-cache-owner=bin              \
            --with-browser=/usr/bin/lynx          \
            --with-vgrind=/usr/bin/vgrind         \
            --with-grap=/usr/bin/grap
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

## 77. Procps-ng-4.0.5

Procps-ng 软件包包含监视进程的程序。

```text
cd /sources;tar -xf procps-ng-4.0.5.tar.xz;cd procps-ng-4.0.5
```

准备编译 Procps-ng：

```text
./configure --prefix=/usr                           \
            --docdir=/usr/share/doc/procps-ng-4.0.5 \
            --disable-static                        \
            --disable-kill                          \
            --enable-watch8bit                      \
            --with-systemd
```

编译该软件包：

```text
time make
```

如果要运行测试套件，执行命令：

```text
chown -R tester .
su tester -c "PATH=$PATH make check"
```

已知名为 ps with output flag bsdtime,cputime,etime,etimes 的一项测试在宿主系统内核未启用 CONFIG_BSD_PROCESS_ACCT 时会失败。

另外，一项 pgrep 测试在 chroot 环境中可能失败。

安装该软件包：

```text
make install
```

## 78. Util-linux-2.40.4

Util-linux 软件包包含若干工具程序。

这些程序中有处理文件系统、终端、分区和消息的工具。

```text
cd /sources;rm -rf util-linux-2.40.4;tar -xf util-linux-2.40.4.tar.xz;cd util-linux-2.40.4
```

准备编译 Util-linux：

```text
./configure --bindir=/usr/bin     \
            --libdir=/usr/lib     \
            --runstatedir=/run    \
            --sbindir=/usr/sbin   \
            --disable-chfn-chsh   \
            --disable-login       \
            --disable-nologin     \
            --disable-su          \
            --disable-setpriv     \
            --disable-runuser     \
            --disable-pylibmount  \
            --disable-liblastlog2 \
            --disable-static      \
            --without-python      \
            ADJTIME_PATH=/var/lib/hwclock/adjtime \
            --docdir=/usr/share/doc/util-linux-2.40.4
```

编译该软件包：

```text
time make
```

创建 /etc/fstab 文件以满足两项测试的要求，并以非 root 用户身份运行测试套件：

```text
touch /etc/fstab
chown -R tester .
su tester -c "make -k check"
```

安装该软件包：

```text
make install
```

## 79. E2fsprogs-1.47.2

E2fsprogs 软件包包含处理 ext2 文件系统的工具。

此外它也支持 ext3 和 ext4 日志文件系统。

```text
cd /sources;tar -xf e2fsprogs-1.47.2.tar.gz;cd e2fsprogs-1.47.2
```

### 79.1 安装 E2fsprogs

E2fsprogs 文档推荐在源代码目录树中的一个子目录内构建该软件包：

```text
mkdir -v build;cd build
```

准备编译 E2fsprogs：

```text
../configure --prefix=/usr           \
             --sysconfdir=/etc       \
             --enable-elf-shlibs     \
             --disable-libblkid      \
             --disable-libuuid       \
             --disable-uuidd         \
             --disable-fsck
```

编译该软件包：

```text
time make
```

执行以下命令，以运行测试：

```text
make check
```

已知一项名为 m_assume_storage_prezeroed 的测试会失败。

已知另一项名为 m_rootdir_acl 的测试在 LFS 使用的文件系统不是 ext4 时可能失败。

安装该软件包：

```text
make install
```

删除无用的静态库：

```text
rm -fv /usr/lib/{libcom_err,libe2p,libext2fs,libss}.a
```

该软件包安装了一个 gzip 压缩的 .info 文件，却没有更新系统的 dir 文件。执行以下命令解压该文件，并更新系统 dir 文件：

```text
gunzip -v /usr/share/info/libext2fs.info.gz
install-info --dir-file=/usr/share/info/dir /usr/share/info/libext2fs.info
```

如果需要，执行以下命令创建并安装一些额外的文档：

```text
makeinfo -o      doc/com_err.info ../lib/et/com_err.texinfo
install -v -m644 doc/com_err.info /usr/share/info
install-info --dir-file=/usr/share/info/dir /usr/share/info/com_err.info
```

### 79.2 配置 E2fsprogs

可以执行命令，从默认的 ext4 特性列表中移除该特性：

```text
sed 's/metadata_csum_seed,//' -i /etc/mke2fs.conf
```
