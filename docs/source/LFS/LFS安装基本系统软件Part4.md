# LFS 安装基本系统软件 Part4

## 1. 关于调试符号

许多程序和库在默认情况下被编译为带有调试符号的二进制文件 (通过使用 gcc 的 -g 选项)。

这意味着在调试这些带有调试信息的程序和库时，调试器不仅能给出内存地址，还能给出子程序和变量的名称。

然而，包含这些调试符号会显著增大程序或库的体积。下面是两个表现调试符号占用空间的例子：

- 一个有调试符号的 bash 二进制程序：1200 KB

- 一个没有调试符号的 bash 二进制程序：480 KB (小 60%)

- 带有调试符号的 Glibc 和 GCC 文件 (/lib 和 /usr/lib 目录中)：87 MB

- 没有调试符号的 Glibc 和 GCC 文件：16 MB (小 82%)

具体的文件大小与使用的编译器和 C 库相关，但是移除调试符号的程序通常比移除调试符号前小 50% 到 80%。

由于大多数用户永远不会用调试器调试系统软件，可以通过移除它们的调试符号，回收大量磁盘空间。

## 2. 移除调试符号

> 本节是可选的。

如果系统不是为程序员设计的，也没有调试系统软件的计划，可以通过从二进制程序和库移除调试符号和不必要的符号表项，将系统的体积减小约
2 GB。

对于一般的 Linux 用户，这不会造成任何不便。

`strip` 命令的 `--strip-unneeded` 选项从程序或库中移除所有调试符号。

它也会移除所有链接器 (对于静态库) 或动态链接器 (对于动态链接的程序和共享库) 不需要的符号表项。

```bash
save_usrlib="$(cd /usr/lib; ls ld-linux*[^g])
             libc.so.6
             libthread_db.so.1
             libquadmath.so.0.0.0
             libstdc++.so.6.0.33
             libitm.so.1.0.0
             libatomic.so.1.2.0"

cd /usr/lib

for LIB in $save_usrlib; do
    objcopy --only-keep-debug --compress-debug-sections=zlib $LIB $LIB.dbg
    cp $LIB /tmp/$LIB
    strip --strip-unneeded /tmp/$LIB
    objcopy --add-gnu-debuglink=$LIB.dbg /tmp/$LIB
    install -vm755 /tmp/$LIB /usr/lib
    rm /tmp/$LIB
done

online_usrbin="bash find strip"
online_usrlib="libbfd-2.44.so
               libsframe.so.1.0.0
               libhistory.so.8.2
               libncursesw.so.6.5
               libm.so.6
               libreadline.so.8.2
               libz.so.1.3.1
               libzstd.so.1.5.7
               $(cd /usr/lib; find libnss*.so* -type f)"

for BIN in $online_usrbin; do
    cp /usr/bin/$BIN /tmp/$BIN
    strip --strip-unneeded /tmp/$BIN
    install -vm755 /tmp/$BIN /usr/bin
    rm /tmp/$BIN
done

for LIB in $online_usrlib; do
    cp /usr/lib/$LIB /tmp/$LIB
    strip --strip-unneeded /tmp/$LIB
    install -vm755 /tmp/$LIB /usr/lib
    rm /tmp/$LIB
done

for i in $(find /usr/lib -type f -name \*.so* ! -name \*dbg) \
         $(find /usr/lib -type f -name \*.a)                 \
         $(find /usr/{bin,sbin,libexec} -type f); do
    case "$online_usrbin $online_usrlib $save_usrlib" in
        *$(basename $i)* )
            ;;
        * ) strip --strip-unneeded $i
            ;;
    esac
done

unset BIN LIB save_usrlib online_usrbin online_usrlib
```

这里会产生关于很多文件的错误信息，因为无法识别这些文件的格式。这些警告可以安全地忽略。

它们表明那些文件是脚本文件，而不是二进制文件。

## 3. 清理系统

最后，清理在执行测试的过程中遗留的一些文件：

```text
rm -rf /tmp/{*,.*}
```

在 /usr/lib 和 /usr/libexec 目录中还有一些扩展名为 .la 的文件。它们是 "libtool 档案" 文件。

现在删除这些文件：

```text
find /usr/lib /usr/libexec -name \*.la -delete
```

之前构建的编译器仍然有一部分安装在系统上，它现在已经没有存在的意义了。执行命令删除它：

```text
find /usr -depth -name $(uname -m)-lfs-linux-gnu\* | xargs rm -rf
```

最后，移除上一章开始时创建的临时 'tester' 用户账户。

```text
userdel -r tester
```
