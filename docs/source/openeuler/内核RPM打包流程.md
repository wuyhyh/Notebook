# 内核 RPM 打包流程

好，那把之前走过的坑都抹掉，给你一份**干净可复现的内核 RPM 打包流程**，从“已经编好内核”到“在板子上用 rpm 升级”。

下面假定：

* 内核源码：`~/tmp-3/openEuler-5.10.0-216-src`
* 交叉编译已经在那里面成功跑过一次 `make ...`，Image、模块、dtb 都是最新的
* rpm 工作目录：`~/rpm-build`

---

## 1. 准备 rpm 构建目录

在 WSL 里执行一次即可：

```bash
mkdir -p ~/rpm-build/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
```

---

## 2. 从内核树导出要打包的内容

### 2.1 获取 kernel release

```bash
cd ~/tmp-3/openEuler-5.10.0-216-src
KREL=$(make kernelrelease)
echo "$KREL"          # 例如：5.10.0-216.oe2203sp4.phytium
```

### 2.2 安装模块到 staging 目录

```bash
sudo rm -rf /tmp/kernel-${KREL}
mkdir -p /tmp/kernel-${KREL}

make ARCH=arm64 CROSS_COMPILE=aarch64-openeuler-linux- \
     modules_install INSTALL_MOD_PATH=/tmp/kernel-${KREL}
```

这一步生成：

```text
/tmp/kernel-${KREL}/lib/modules/${KREL}/...
```

### 2.3 拷贝 Image 和 DTB

按你当前的内核输出路径来：

```bash
mkdir -p /tmp/kernel-${KREL}/boot/dtb-${KREL}

cp arch/arm64/boot/Image \
   /tmp/kernel-${KREL}/boot/Image-${KREL}

# dts 目录按你板子实际调整
cp arch/arm64/boot/dts/phytium/*.dtb \
   /tmp/kernel-${KREL}/boot/dtb-${KREL}/
```

此时 staging 目录结构如下：

```text
/tmp/kernel-${KREL}/
  ├── boot/
  │   ├── Image-${KREL}
  │   └── dtb-${KREL}/*.dtb
  └── lib/
      └── modules/
          └── ${KREL}/...
```

### 2.4 打一个源码归档给 rpmbuild 用

```bash
cd /tmp
tar czf ~/rpm-build/SOURCES/kernel-${KREL}.tar.gz kernel-${KREL}
```

---

## 3. 编写 spec 文件

新建：`~/rpm-build/SPECS/kernel-custom-phytium.spec`

内容用这一版（就是你刚才成功生成 715M rpm 的版本）：

```spec
# 关闭自动 strip/debug/os_install_post，避免在 x86 上 strip ARM64 .ko
%global __strip /bin/true
%global __debug_install_post %{nil}
%global __os_install_post %{nil}

# 如果外面没传 krel，则用默认值
%{!?krel:%define krel 5.10.0-custom}

Name:           kernel-custom-phytium
Version:        5.10.0
Release:        1%{?dist}
Summary:        Custom Phytium kernel %{krel}
License:        GPLv2
BuildArch:      noarch
Source0:        kernel-%{krel}.tar.gz

%description
Custom cross-built kernel Image, modules and device trees for Phytium D2000 board.

%prep
%setup -q -n kernel-%{krel}

%build
# Nothing to build: we just repackage prebuilt kernel, modules and dtbs.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
# 只拷贝 boot 和 lib，两棵树结构保持不变
cp -a boot lib %{buildroot}/

%files
/boot/Image-%{krel}
/boot/dtb-%{krel}
/lib/modules/%{krel}
```

说明：

* `%global __strip /bin/true` 等三行关闭了 rpmbuild 的自动 strip/debug 处理，避免 x86 的 `/usr/bin/strip` 去“处理” ARM64 模块。
* `BuildArch: noarch`，因为包本身只是“数据”，在 x86 上打包、在 arm64 上安装都是可以的。
* 安装后系统上会出现 `/boot/Image-${KREL}`、`/boot/dtb-${KREL}` 目录和 `/lib/modules/${KREL}`。

---

## 4. 运行 rpmbuild 生成 rpm

在 rpm-build 目录下执行：

```bash
cd ~/rpm-build

# 再取一次 KREL，保证和打 tar 时一致
KREL=$(cd ~/tmp-3/openEuler-5.10.0-216-src && make kernelrelease)

rpmbuild -bb SPECS/kernel-custom-phytium.spec \
    --define "_topdir $HOME/rpm-build" \
    --define "krel ${KREL}"
```

等待几分钟（主要是在复制和打包几万文件），完成后可以看到：

```bash
ls -lh ~/rpm-build/RPMS/noarch
# 例如：
# kernel-custom-phytium-5.10.0-1.noarch.rpm  (约 700M+)
```

你截图里的那颗 715M 的 rpm 就是这一步的结果。

---

## 5. 在开发板上使用 rpm 升级内核

1. 复制 rpm 到板子：

   ```bash
   scp ~/rpm-build/RPMS/noarch/kernel-custom-phytium-5.10.0-1.noarch.rpm \
       root@192.168.11.105:/root/
   ```

2. 板子上安装（根据你想保留还是覆盖旧内核，选择 `-i` 或 `-U`）：

   ```bash
   cd /root
   rpm -ivh kernel-custom-phytium-5.10.0-1.noarch.rpm    # 安装新版本，保留旧版本
   # 或
   # rpm -Uvh kernel-custom-phytium-5.10.0-1.noarch.rpm  # 就地升级
   ```

   完成后，系统里会出现：

   ```text
   /boot/Image-${KREL}
   /boot/dtb-${KREL}/*.dtb
   /lib/modules/${KREL}/...
   ```

3. 手工更新 U-Boot 启动参数（按你现在的流程）：

    * 把 `boot` 命令里的内核文件改为 `Image-${KREL}`；
    * dtb 路径改为 `dtb-${KREL}/your-board.dtb`；
    * 保存 env，重启验证。

---

## 6. 可以给实习生的一页版命令清单

最后整理成一条流水线（假设已经交叉编译成功）：

```bash
# 1) 准备 staging
cd ~/tmp-3/openEuler-5.10.0-216-src
KREL=$(make kernelrelease)

sudo rm -rf /tmp/kernel-${KREL}
mkdir -p /tmp/kernel-${KREL}

make ARCH=arm64 CROSS_COMPILE=aarch64-openeuler-linux- \
     modules_install INSTALL_MOD_PATH=/tmp/kernel-${KREL}

mkdir -p /tmp/kernel-${KREL}/boot/dtb-${KREL}
cp arch/arm64/boot/Image \
   /tmp/kernel-${KREL}/boot/Image-${KREL}
cp arch/arm64/boot/dts/phytium/*.dtb \
   /tmp/kernel-${KREL}/boot/dtb-${KREL}/

cd /tmp
tar czf ~/rpm-build/SOURCES/kernel-${KREL}.tar.gz kernel-${KREL}

# 2) rpmbuild
cd ~/rpm-build
rpmbuild -bb SPECS/kernel-custom-phytium.spec \
    --define "_topdir $HOME/rpm-build" \
    --define "krel ${KREL}"

# 3) 结果
ls -lh ~/rpm-build/RPMS/noarch/*.rpm
```

这样，这条“交叉编译 → 打包成 rpm → 板子上升级内核”的链路就固定下来了。
后续你换内核配置或打上新补丁，只要重新编一次内核，然后重复 2/3/4 步，就能生成新的升级包。

