# openEuler用户态chroot环境搭建

## 1. 目录规划（全部放在 `~/euler` 下）

目标目录结构：

```text
~/euler
  ├── bin/          # 脚本：oe-chroot.sh / oe-umount.sh
  ├── oe-root/      # openEuler aarch64 rootfs（chroot 根目录）
  ├── oe-work/      # 你的源码、spec 等，host + chroot 共享
  ├── iso/          # 用来挂载 openEuler ISO（可选）
  └── oe-rootfs.tar # 从 docker 导出的 rootfs tar 包
```

先在宿主 WSL（Ubuntu）里建好：

```bash
cd ~
mkdir -p euler/{bin,oe-root,oe-work,iso}
```

后面所有命令都默认在宿主里从 `~/euler` 开始。

---

## 2. 宿主：准备基础工具（qemu / binfmt / docker）

这些你大部分已经装过了，这里整理一版，重复执行也没关系。

```bash
sudo apt update
sudo apt install -y qemu-user-static binfmt-support docker.io
```

检查 binfmt 里有没有 aarch64：

```bash
ls /proc/sys/fs/binfmt_misc
# 如果里面有 qemu-aarch64 就行
```

如果没有：

```bash
sudo update-binfmts --enable qemu-aarch64
```

---

## 3. 宿主：用 Docker 拉 openEuler aarch64 并导出 rootfs

仍然在宿主里：

```bash
cd ~/euler
```

1. 拉镜像（aarch64 版本的 22.03-SP4）

```text
sudo docker pull --platform=linux/arm64 openeuler/openeuler:22.03-lts-sp4
```

2. 创建一个临时容器（WARNING 是正常的，忽略，只要有个容器 ID 输出即可）

```text
sudo docker create --name oe_aarch64_tmp openeuler/openeuler:22.03-lts-sp4
```

3. 导出 rootfs 到 tar 包

```text
sudo docker export oe_aarch64_tmp -o oe-rootfs.tar
```

4. 删除临时容器

```text
sudo docker rm oe_aarch64_tmp
```

确认 tar 包存在：

```bash
ls -lh oe-rootfs.tar
```

---

## 4. 宿主：把 rootfs 解压到 `oe-root`，拷 qemu

```bash
cd ~/euler
sudo tar -xf oe-rootfs.tar -C oe-root

# 把 qemu-aarch64-static 拷到 rootfs 里
sudo cp -v /usr/bin/qemu-aarch64-static oe-root/usr/bin/
```

此时 `~/euler/oe-root` 就是一个完整的 openEuler aarch64 文件系统。

---

## 5. 宿主：创建进入 / 退出 chroot 的脚本（放在 `~/euler/bin`）

关键点：

* 脚本通过自身路径自动找到 `~/euler`，不依赖 `$HOME`；
* 外面执行 `~/euler/bin/oe-chroot.sh`，脚本自动用 `sudo` 重新执行为 root；
* 脚本内部 **不再调用 sudo**，避免你之前遇到的 pty 问题。

### 5.1 `oe-chroot.sh`

```bash
cd ~/euler

cat > bin/oe-chroot.sh << 'EOF'
#!/usr/bin/env bash
set -e

# 计算 BASE = 脚本所在目录的上一级，例如 ~/euler
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOTFS="$BASE/oe-root"
WORKDIR="$BASE/oe-work"

# 如果当前不是 root，就用 sudo 重新执行自己
if [ "$(id -u)" -ne 0 ]; then
    exec sudo "$0" "$@"
fi

if [ ! -d "$ROOTFS" ]; then
    echo "Rootfs not found at $ROOTFS"
    exit 1
fi

# 挂载 pseudo fs
mount -t proc /proc "$ROOTFS/proc" 2>/dev/null || true
mount -t sysfs sys "$ROOTFS/sys" 2>/dev/null || true
mount -o bind /dev "$ROOTFS/dev" 2>/dev/null || true

mkdir -p "$ROOTFS/dev/pts"
mount -t devpts devpts "$ROOTFS/dev/pts" 2>/dev/null || true

mount -o bind /run "$ROOTFS/run" 2>/dev/null || true

# DNS
cp /etc/resolv.conf "$ROOTFS/etc/resolv.conf"

# /work 共享目录
mkdir -p "$WORKDIR"
mkdir -p "$ROOTFS/work"
mount -o bind "$WORKDIR" "$ROOTFS/work" 2>/dev/null || true

# 进入 chroot（默认 root 身份）
chroot "$ROOTFS" /usr/bin/env -i \
    HOME=/root \
    TERM="$TERM" \
    PS1='(oe-aarch64-chroot) \u@\h:\w\$ ' \
    PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    /bin/bash --login
EOF

chmod +x bin/oe-chroot.sh
```

### 5.2 `oe-umount.sh`（清理挂载）

```bash
cat > bin/oe-umount.sh << 'EOF'
#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOTFS="$BASE/oe-root"

if [ "$(id -u)" -ne 0 ]; then
    exec sudo "$0" "$@"
fi

for m in mnt/oeiso work dev/pts dev proc sys run; do
    if mountpoint -q "$ROOTFS/$m"; then
        umount "$ROOTFS/$m"
    fi
done
EOF

chmod +x bin/oe-umount.sh
```

---

## 6. 第一次进入 chroot，验证环境

在宿主里：

```bash
cd ~/euler
./bin/oe-chroot.sh
```

脚本会自己用 sudo 提权，然后你应该看到类似：

```text
(oe-aarch64-chroot) root@Tokamark-2:/#
```

在 chroot 里执行：

```bash
uname -m
file /bin/bash
```

正常应该都显示 `aarch64`，这说明 aarch64 chroot 工作正常。

接下来这段都在 chroot 里执行。

---

## 7. 在 chroot 里初始化构建环境（root 身份）

注意：**在 chroot 里面不要用 sudo**，root 就够了。
更新缓存

```bash
dnf makecache
```

安装开发工具和 rpmbuild 需要的包

```text
dnf groupinstall -y "Development Tools"
```

```text
dnf install -y \
    rpm-build rpmdevtools dnf-plugins-core \
    ncurses-devel openssl-devel bc flex bison \
    elfutils-libelf-devel dwarves git which tar xz
```

```text
dnf groupinstall "Minimal Install"
```

### 4.1 基础系统组件

在 chroot 里：

尽量避免拉内核包，纯用户态

```text
dnf groupinstall "Minimal Install"
```

```text
dnf install \
systemd systemd-udev \
dnf \
openssh-server \
sudo passwd \
vim-minimal bash-completion less \
iproute iputils net-tools \
procps-ng psmisc \
pciutils lsof \
rsyslog chrony \
tar gzip bzip2 xz \
e2fsprogs xfsprogs
```

如果 groupinstall 把 kernel-core 拉进来了，可以后面再删掉，反正你最后要用自己的内核。

创建构建用的普通用户（以后专门用来跑 rpmbuild）：

```bash
useradd -m builder
# 不要配置 sudo，没意义，qemu chroot 里 sudo 提不了权

su - builder
rpmdev-setuptree
```

现在 `builder` 用户的目录里有：

```text
~/rpmbuild/
  ├── BUILD
  ├── RPMS
  ├── SOURCES
  ├── SPECS
  └── SRPMS
```

`/work` 目录就是宿主的 `~/euler/oe-work`，可以在宿主 git clone，然后在 chroot 里直接看到。

---

## 8. ISO 作为本地 RPM 仓库（可选，但你手上已经有 ISO，可以用）

你说“所有东西放在 ~/euler 下”，那我们就把 ISO 也挂在这里。

### 8.1 宿主里挂载 ISO，并绑定到 chroot

在宿主（不是 chroot）：

```bash
cd ~/euler

# 1) 假设 ISO 在 ~/euler/openEuler-22.03-LTS-SP4-everything-aarch64-dvd.iso
sudo mount -o loop openEuler-22.03-LTS-SP4-everything-aarch64-dvd.iso iso

# 2) 把它绑到 chroot 的 /mnt/oeiso
sudo mkdir -p oe-root/mnt/oeiso
sudo mount --bind iso oe-root/mnt/oeiso
```

以后如果要清理，用 `./bin/oe-umount.sh` 就行。

### 8.2 在 chroot 里配置 repo

再进 chroot（宿主执行 `./bin/oe-chroot.sh`），在 chroot 里：

```bash
ls /mnt/oeiso
# 能看到 OS/、Packages/ 等目录就对了

cat > /etc/yum.repos.d/oe-iso.repo << 'EOF'
[oe-iso]
name=openEuler-22.03-LTS-SP4-everything-aarch64-dvd
baseurl=file:///mnt/oeiso/OS/
enabled=1
gpgcheck=0
EOF

dnf clean all
dnf repolist
```

现在 chroot 里的 dnf 就可以从你的 ISO 里装包了。

---

## 9. 之后的日常使用流程（总结）

1. 宿主准备源码和 spec（都放 `~/euler/oe-work`）：

   ```bash
   cd ~/euler/oe-work
   git clone ... linux-phytium
   cp xxx.spec specs/
   ```

2. 需要用 ISO 时：

   ```bash
   cd ~/euler
   ./bin/oe-umount.sh          # 可选，清理旧挂载
   sudo mount -o loop openEuler-22.03-LTS-SP4-everything-aarch64-dvd.iso iso
   sudo mkdir -p oe-root/mnt/oeiso
   sudo mount --bind iso oe-root/mnt/oeiso
   ```

3. 进入 chroot（root）：

   ```bash
   cd ~/euler
   ./bin/oe-chroot.sh
   ```

4. 在 chroot 里：

    * 系统级操作：用 root；
    * 真正打包时：

      ```bash
      su - builder
      cd /work/linux-phytium
      tar --exclude-vcs -czf ~/rpmbuild/SOURCES/linux-phytium.tar.gz .
      cp /work/specs/linux-phytium.spec ~/rpmbuild/SPECS/
      cd ~/rpmbuild/SPECS
      rpmbuild -ba linux-phytium.spec
      ```

5. 打好的 RPM 在宿主路径：

   ```bash
   ~/euler/oe-root/home/builder/rpmbuild/RPMS/aarch64/
   ```

6. 不用了可以在宿主执行：

   ```bash
   cd ~/euler
   ./bin/oe-umount.sh
   sudo umount iso  # 如果不再需要 ISO 挂载
   ```
