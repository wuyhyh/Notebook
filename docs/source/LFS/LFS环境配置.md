# 环境检测脚本

在 fedora server 42上编译 [LFS](https://lfs.xry111.site/zh_CN/12.3-systemd/)

## yacc is not Bison 的问题

1. 构建包装器

放一个 wrapper 到 /usr/bin（推荐）

作为 root 执行：

- 确保 bison 已安装（你已装好，可跳过）

```text
dnf install -y bison
```

- 写一个兼容的 yacc 包装脚本

```text
install -d /usr/bin
cat > /usr/bin/yacc <<'EOF'
#!/bin/sh
exec bison -y "$@"
EOF
chmod +x /usr/bin/yacc
```

- 验证 PATH 与版本

```text
command -v yacc
yacc --version   # 应显示 bison 的版本
```

说明：大多数系统 /usr/local/bin 默认在 /usr/bin 之前，这样 yacc 会先命中你新建的 wrapper。

## 工具版本检测脚本

[version-check.sh](./version-check.sh)

```bash
#!/bin/bash
# A script to list version numbers of critical development tools

# If you have tools installed in other directories, adjust PATH here AND
# in ~lfs/.bashrc (section 4.4) as well.

LC_ALL=C 
PATH=/usr/bin:/bin

bail() { echo "FATAL: $1"; exit 1; }
grep --version > /dev/null 2> /dev/null || bail "grep does not work"
sed '' /dev/null || bail "sed does not work"
sort   /dev/null || bail "sort does not work"

ver_check()
{
   if ! type -p $2 &>/dev/null
   then 
     echo "ERROR: Cannot find $2 ($1)"; return 1; 
   fi
   v=$($2 --version 2>&1 | grep -E -o '[0-9]+\.[0-9\.]+[a-z]*' | head -n1)
   if printf '%s\n' $3 $v | sort --version-sort --check &>/dev/null
   then 
     printf "OK:    %-9s %-6s >= $3\n" "$1" "$v"; return 0;
   else 
     printf "ERROR: %-9s is TOO OLD ($3 or later required)\n" "$1"; 
     return 1; 
   fi
}

ver_kernel()
{
   kver=$(uname -r | grep -E -o '^[0-9\.]+')
   if printf '%s\n' $1 $kver | sort --version-sort --check &>/dev/null
   then 
     printf "OK:    Linux Kernel $kver >= $1\n"; return 0;
   else 
     printf "ERROR: Linux Kernel ($kver) is TOO OLD ($1 or later required)\n" "$kver"; 
     return 1; 
   fi
}

# Coreutils first because --version-sort needs Coreutils >= 7.0
ver_check Coreutils      sort     8.1 || bail "Coreutils too old, stop"
ver_check Bash           bash     3.2
ver_check Binutils       ld       2.13.1
ver_check Bison          bison    2.7
ver_check Diffutils      diff     2.8.1
ver_check Findutils      find     4.2.31
ver_check Gawk           gawk     4.0.1
ver_check GCC            gcc      5.2
ver_check "GCC (C++)"    g++      5.2
ver_check Grep           grep     2.5.1a
ver_check Gzip           gzip     1.3.12
ver_check M4             m4       1.4.10
ver_check Make           make     4.0
ver_check Patch          patch    2.5.4
ver_check Perl           perl     5.8.8
ver_check Python         python3  3.4
ver_check Sed            sed      4.1.5
ver_check Tar            tar      1.22
ver_check Texinfo        texi2any 5.0
ver_check Xz             xz       5.0.0
ver_kernel 5.4 

if mount | grep -q 'devpts on /dev/pts' && [ -e /dev/ptmx ]
then echo "OK:    Linux Kernel supports UNIX 98 PTY";
else echo "ERROR: Linux Kernel does NOT support UNIX 98 PTY"; fi

alias_check() {
   if $1 --version 2>&1 | grep -qi $2
   then printf "OK:    %-4s is $2\n" "$1";
   else printf "ERROR: %-4s is NOT $2\n" "$1"; fi
}
echo "Aliases:"
alias_check awk GNU
alias_check yacc Bison
alias_check sh Bash

echo "Compiler check:"
if printf "int main(){}" | g++ -x c++ -
then echo "OK:    g++ works";
else echo "ERROR: g++ does NOT work"; fi
rm -f a.out

if [ "$(nproc)" = "" ]; then
   echo "ERROR: nproc is not available or it produces empty output"
else
   echo "OK: nproc reports $(nproc) logical cores are available"
fi
```

## 使用中科大镜像源

1. 下载列表/校验文件

先手动下载 wget-list-systemd 和 md5sums

2. 把每行 URL 替换为 “USTC 基址 + 文件名”

```text
sed -E 's|.*/([^/]+)$|https://mirrors.ustc.edu.cn/lfs/lfs-packages/12.3/\1|' wget-list-systemd > wget-list-ustc
```

3. 下载（可断点续传）

```text
wget --input-file=wget-list-ustc --continue --directory-prefix="$LFS/sources"
```

4. 校验

```text
cp md5sums "$LFS/sources/"
pushd "$LFS/sources"; md5sum -c md5sums; popd
```
