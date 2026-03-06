# 构建发布内核 RPM 包

目标：在 ARM 架构环境（虚拟机/服务器）上，使用 openEuler 内核源码，自动化构建内核 RPM 包

> 参考的 openEuler
[官方文档](https://docs.openeuler.org/zh/docs/22.03_LTS_SP4/server/development/application_dev/building_an_rpm_package.html)

## 1. 手动打包 RPM

### 1.1 安装需要的包,环境

1. 安装依赖包：

```bash
dnf install rpmdevtools
```

2. 创建一套套标准化的“工作空间”

```bash
rpmdev-setuptree
```

3. 目录结构说明

执行以下命令：

```bash
tree rpmbuild
```

`rpmbuild` 目录的结构如下：

```text
$ tree rpmbuild
  rpmbuild
  ├── BUILD
  ├── RPMS
  ├── SOURCES
  ├── SPECS
  └── SRPMS
  ```

---

### 1.2 使用步骤

1. 将源码压缩包和配置文件放在 SOURCES：

```bash
cp /root/openeuler-5.10.0-136-src-master.tar.gz ~/rpmbuild/SOURCES/
cp ~/config-5.10.0-136.12.0.86.aarch64 ~/rpmbuild/SOURCES/
```

2. 将 `openeuler-kernel.spec` 放在 SPECS：
* `openeuler-kernel.spec` 文件内容见1.3小节

```bash
cd ~/rpmbuild/SPECS/ 
vim openeuler-kernel.spec
```

3. 构建 RPM：

```bash
cd ~/rpmbuild/SPECS
rpmbuild -bb openeuler-kernel.spec
```

> `-bb`选项：通过specfile文件构建二进制包。
>
>`-ba`选项：通过specfile文件构建源码包和二进制包。

4. 成功后查看生成的包：

```
~/rpmbuild/RPMS/aarch64/
- kernel-5.10.0_136.custom*.rpm
- kernel-devel-5.10.0_136.custom*.rpm
- kernel-headers-5.10.0_136.custom*.rpm
```

---

### 1.3 spec 文件

```spec
# ================================
# 关闭 debuginfo（发行版模板）
# ================================
%global debug_package %{nil}
%global _enable_debug_packages 0
%global _missing_build_ids_terminate_build 0
# 内核 rpm-pkg 不使用 BUILDROOT，关闭所有 brp
%global __os_install_post %{nil}
%global _build_id_links none

Name:           openeuler-kernel
Version:        5.10.0
Release:        136.custom%{?dist}
Summary:        OpenEuler 5.10.0-136 内核
Summary(zh_CN): OpenEuler 5.10.0-136 内核
License:        GPLv2
URL:            https://openeuler.org
Source0:        openeuler-5.10.0-136-src-master.tar.gz
BuildArch:      aarch64

# 内核编译依赖
BuildRequires:  gcc make bc flex bison perl elfutils-libelf-devel ncurses-devel
# 运行时依赖可留空，如需添加可以写在下面
# Requires:

%description
OpenEuler 5.10.0-136 内核源码包，用于生成内核、内核开发包和内核头文件包。

%description -l zh_CN
OpenEuler 5.10.0-136 内核源码包，用于生成内核、内核开发包和内核头文件包。

%prep
# 解压源码压缩包
%setup -q -n openeuler-5.10.0-136-src-master

# 使用已有的内核配置文件
# 注意：确保这个文件已经放到 SOURCES 目录
cp %{_sourcedir}/config-5.10.0-136.12.0.86.aarch64 .config

%build
cd %{_builddir}/openeuler-5.10.0-136-src-master

# 自动处理新选项（可选，但保险）
make olddefconfig ARCH=arm64 

# 构建内核 RPM（生成 kernel / kernel-devel / kernel-headers）
make ARCH=arm64 %{?_smp_mflags} rpm-pkg LOCALVERSION=-136.custom


%install
# 内核源码包通常不做 install，生成的 rpm 会放在 RPMS 目录
rm -rf %{buildroot}


%changelog
* Wed Jan 14 2026 Your Name <youremail@example.com> - 5.10.0-136.custom-1
- 初始打包
```

---

## 2. rmp包自动化脚本

### 2.1 创建脚本

```bash
vim build-openeuler-kernel-rpm.sh
```

### 2.2 赋予可执行权限

```bash
chmod +x build-openeuler-kernel-rpm.sh
```

### 2.3 脚本使用方式

1. 直接执行
    ```bash
   ./build-openeuler-kernel-rpm.sh
   ``` 
    * 条件：对应目录存在
   ```bash
   DEFAULT_SRC_TARBALL="/root/openeuler-5.10.0-136-src-master.tar.gz"
   DEFAULT_KCONFIG="$HOME/config-5.10.0-136.12.0.86.aarch64"
    ```
2. 指定版本号
   ```bash
   ./build-openeuler-kernel-rpm.sh "" "" 136.custom
   ``` 
3. 源码压缩包路径、配置文件路径、版本号、额外配置内核全部自定义
   ```bash
   ./build-openeuler-kernel-rpm.sh \
     /data/kernel-src.tar.gz \
     /data/config.arm64 \
     136.custom \
     /root/kcfg/my_custom.cfg
   ```
---
### 2.4 生成内容：

```text
~/rpmbuild/RPMS/aarch64/
  ├── kernel-5.10.0_136.custom-*.rpm
  ├── kernel-devel-5.10.0_136.custom-*.rpm
  └── kernel-headers-5.10.0_136.custom-*.rpm
```

```bash
build-openeuler-kernel-rpm.sh
```
