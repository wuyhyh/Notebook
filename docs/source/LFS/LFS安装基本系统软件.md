# LFS 安装基本系统软件

## 1. 首先进入 chroot

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

## 2. Man-pages-6.12

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

## 3. Iana-Etc-20250123


