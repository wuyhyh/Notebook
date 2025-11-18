# oebuild 构建系统

openEuler Embeddedd的核心构建系统是基于Yocto，但又根据自身的需求做了很多定制化的开发。

社区：

[飞腾 bsp](https://gitee.com/phytium_embedded/phytium-openeuler-embedded-bsp)

[Phytium CPU OpenEuler Embedded 用户使用手册](https://gitee.com/phytium_embedded/phytium-embedded-docs/tree/master/linux)

[oe-build](https://pages.openeuler.openatom.cn/embedded/docs/build/html/openEuler-22.03-LTS-SP4/yocto/index.html)

## 0. 安装 WSL 虚拟机

选择的发行版为 Ubuntu 24.04 LTS

在以管理员身份运行的 powershell 中：

```text
wsl --list --online
wsl --install -d Ubuntu-24.04
```

安装的时候会提示输入 `username` 和 `password`。

## 1. 创建独立的 python 虚拟环境

在 Ubuntu 24.04 中

先进行一下 Git 相关的基本配置

```text
git config --global user.name wuyhyh
git config --global user.email wuyhyh@gmail.com
git config --global core.editor vim
```

创建工程目录

```text
mkdir -p ~/openeuler
```

安装 python 虚拟环境

```text
sudo apt update
sudo apt install -y python3-venv python3-full build-essential
```

建立编译工程的虚拟环境

```text
python3 -m venv ~/venvs/oebuild
source ~/venvs/oebuild/bin/activate
```

升级 pip 并安装 oebuild

```text
python -m pip install --upgrade pip
pip install oebuild
```

验证

```text
which oebuild
oebuild --help
```

退出环境

```text
deactivate
```

## 2. 安装 docker

先把 WSL 打开 systemd

```text
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
```

关闭重启 wsl
在 powershell中执行

```text
wsl --shutdown
```

重新进入项目

```text
cd ~/openeuler
source ~/venvs/oebuild/bin/activate
```

安装 docker

```text
sudo apt install -y docker.io
```

把我们自己加入 docker 组，这样就不用每次 sudo 了

```text
sudo usermod -aG docker $USER
newgrp docker
```

启动并设为开机自启

```text
sudo systemctl enable --now docker
```

验证，看是否输出
`Hello from Docker!`

```text
docker run --rm hello-world
```

## 3. 运行 oebuild

### 3.1 初始化工作目录

`oebuild init` 命令会初始化工作目录

```text
oebuild init -b openEuler-24.03-LTS workdir
cd ~/openeuler/workdir
```

### 3.2 创建编译配置

`oebuild update` 命令会下载目标版本的项目源码及构建容器

```text
oebuild update
```

## 4. 获取飞腾软件包

```text
rm -rvf src/yocto-meta-openeuler/bsp/meta-phytium
```

```text
git clone https://gitee.com/phytium_embedded/phytium-bsp-openeuler-embedded.git \
src/yocto-meta-openeuler/bsp/meta-phytium
```

```text
cp -v src/yocto-meta-openeuler/bsp/meta-phytium/phytium.yaml src/yocto-meta-openeuler/.oebuild/platform/
```

## 5. 开始 oebuild 构建

### 5.1 增大 swap 区，如果 wsl 内存够大（16G+）可以跳过

开始编译之前调大 wsl 的可交换内存

```text
# 查看当前内存和swap
free -h

# 创建8GB swap文件
sudo dd if=/dev/zero of=/swapfile bs=1G count=8
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 确认启用
swapon --show
```

### 5.2 开始编译

激活 python 环境

```text
source ~/venvs/oebuild/bin/activate
```

生成工程目录

```text
cd ~/openeuler/workdir
oebuild generate -p phytium
```

为了后续方便，到 `~` 创建一个指向构建目录的软连接 `phytium_build`

```text
cd ~;
ln -s ~/openeuler/workdir/build/phytium phytium_build
```

进入构建目录启动全量构建：

```text
cd ~/phytium_build
oebuild bitbake openeuler-image
```

使用 Intel 13400 16线程的 CPU 编译时间约为 45 分钟。

## 6. 产物

编译出 **kernel image ,rootfs ,dtb ,iso and phydisk.img**

```text
cd ~/openeuler/workdir/build/phytium/tmp/deploy/images/phytium
```

在 `phytium_build` 下创建一个软连接方便获取镜像文件

```text
cd ~/phytium_build
ln -s ~/openeuler/workdir/build/phytium/tmp/deploy/images/phytium images
```

添加镜像文件路径环境变量方便访问文件：

```text
echo 'export images_path=~/openeuler/workdir/build/phytium/tmp/deploy/images/phytium' >> bashrc
source ~/.bashrc
```

- 内核 `Image`
- 设备树 `pd2008-devboard-dsk.dtb`
- 根文件系统 `openeuler-image-phytium.tar.bz2`

> 以上流程构建出的镜像文件是默认配置，我们需要根据我们的嵌入式平台做定制化修改

## 7. 修改设备树

### 7.1 源码目录

内核源码目录分为两个，分别为他们创建软连接。

```text
cd phytium_build
ln -s /home/wuyuhang/openeuler/workdir/build/phytium/tmp/work/phytium-openeuler-linux/linux-openeuler/5.10-r0/build/ dirty_kernel_src
ln -s /home/wuyuhang/openeuler/workdir/build/phytium/tmp/work-shared/phytium/kernel-source/ pure_kernel_src
```

我们在 `pure_kernel_src` 目录下修改内核代码，并提交 commit message，生成补丁。
每次构建后 `pure_kernel_src` 会回到最初的状态

`dirty_kernel_src` 目录下可以看到生成的配置项 `.config`，方便我们检查内核编译开关。

### 7.2 修改设备树

这是 phytium
嵌入式软件部提供的修改设备树的[方法](https://gitee.com/phytium_embedded/phytium-openeuler-embedded-bsp/wikis/%E5%A6%82%E4%BD%95%E4%BF%AE%E6%94%B9%E7%BC%96%E8%AF%91%E8%AE%BE%E5%A4%87%E6%A0%91)

#### 7.2.1 先进入 Linux 内核源码目录

```text
cd ~/phytium_build/pure_kernel_src
```

设备树在 arch 子目录下

```text
cd arch/arm64/boot/dts/phytium/
```

#### 7.2.2 新增和修改设备树

D2000 CPU 使用pd2008前缀的dtb文件。

将设备树文件复制到源码的设备树目录下完成设备树的**新增**：

```text
cp -v ~/device-tree/pd2008-generic-psci-soc.dtsi ./
cp -v ~/device-tree/pd2008-devboard-dsk.dts ./
```

如果要修改设备树的内容，
例如添加节点, 修改文件 `arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dts`

#### 7.2.3 修改 Makefile

增加的文件要编译需要修改这个目录下的 Makefile，添加新增的设备树文件名

```text
vim Makefile
```

新增目标文件

```text
## d2000 dev board:
dtb-$(CONFIG_ARCH_PHYTIUM) += pd2008-devboard-dsk.dtb
```

#### 7.2.4 修改编译配方

```text
cd ~/openeuler/workdir/src/yocto-meta-openeuler/bsp/meta-phytium/conf/machine/include/
vim phy-base.inc
```

在 `KERNEL_DEVICETREE` 字段增加我们的新设备树 `pd2008-devboard-dsk.dtb`

```text
KERNEL_DEVICETREE ??= " \
    phytium/pe2202-demo-ddr4.dtb \
    phytium/pe2201-demo-ddr4.dtb \
    phytium/pe2204-demo-ddr4.dtb \
    phytium/phytiumpi_firefly.dtb \
    phytium/pd2008-devboard-dsk.dtb \
    "
```

### 7.3 生成补丁

回到源码目录

```text
cd ~/phytium_build/pure_kernel_src
```

生成设备树补丁

```text
git add .
git commit -s -m "update d2000 dtb"
git format-patch -1
```

生成的补丁：**0001-update-d2000-dtb.patch**

> 注意：commit message 会影响补丁的名称。

### 7.4 修改内核构建配方

建立一个进入配方目录的软链接

```text
cd ~/phytium_build
ln -s ~/openeuler/workdir/src/yocto-meta-openeuler/bsp/meta-phytium/recipes-kernel/linux/ bbapend
```

`~/phytium_build/bbappend` 目录下的 `files` 目录存放补丁，`linux-openeuler.bb` 文件是编译配方文件

#### 7.4.1 将补丁放到构建系统的 src 子目录中

```text
cp -v 0001-update-d2000-dtb.patch ~/phytium_build/bbappend/files/
```

#### 7.4.2 修改配方

```text
vim ~/phytium_build/bbappend/linux-openeuler.bbappend
```

加入以下内容

```text
SRC_URI:append = "\
file://0001-update-d2000-dtb.patch \
"
```

### 7.5 重新编译内核

```text
source ~/venvs/oebuild/bin/activate;cd ~/phytium_build
```

启动构建环境：

```text
oebuild bitbake 
```

清理并重新构建

```text
bitbake -c cleansstate linux-openeuler
bitbake linux-openeuler
```

## 8. 修改定制 Linux 内核功能

### 8.1 在 oebuild 中配置内核选项

先进入平台目录，进入构建环境

```text
source ~/venvs/oebuild/bin/activate;cd ~/phytium_build
oebuild bitbake
```

打开 menuconfig

```text
bitbake -c menuconfig linux-openeuler
```

> 注意 menuconfig 的配置在全量构建的时候可能会“失忆”，回退到默认配置，我们需要将差异片段导出
> 然后将差异片段放到配方中让构建工具吸收我们的配置。

生成“最小差异片段”：

```text
bitbake -c diffconfig linux-openeuler
```

> 该任务会把你相对内核基线的改动打印成一个极小的配置片段（只包含变更项，形如 `CONFIG_X=y / # CONFIG_Y is not set`）
>
> **fragment.cfg**

创建一个指向差异文件目录的软链接（退出 `oebuild` 之后做）：

```text
ln -s ~/openeuler/build/phytium/tmp/work/phytium-openeuler-linux/linux-openeuler/5.10-r0 fragment
```

### 8.2 修改配方文件

#### 8.2.1 处理配置片段文件

将配置片段放到配方文件搜索路径下，构建时吸收有差异的内核配置项

```text
cd ~/phytium_build/fragment
```

根据配置修改配置片段的名称，比如打开 `INFINIBAND` 支持：

```text
cp fragment.cfg fragment-infiniband.cfg
```

将配置片段放到构建系统的 src 子目录中

```text
cp -v fragment-infiniband.cfg ~/phytium_build/bbappend/files/
```

#### 8.2.2 修改配方

```text
vim ~/phytium_build/bbappend/linux-openeuler.bbappend
```

在 `linux-openeuler.bb` 文件中增加这三个字段：

```text
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += " \
        file://fragment-infiniband.cfg \
"

KERNEL_CONFIG_FRAGMENTS += " \
        fragment-infiniband.cfg \
"
```

### 8.3 清理并重新构建内核

清理并重新构建内核

```text
bitbake -c cleansstate linux-openeuler
bitbake linux-openeuler
```

全量构建

```text
bitbake openeuler-image
```

退出构建环境

```text
exit
```

### 8.4 内核模块部署到根文件系统

* 内核模块标准放置位置（在目标机上）：`/lib/modules/$(uname -r)/**`。
* 但 **只有当你全量构建镜像**（`bitbake <你的镜像>`）并且镜像“要安装这些模块”时，模块才会被放进根文件系统。
* 你只编译内核（`bitbake linux-openeuler`）时，Yocto 只会生成**模块软件包**，不会改你的 rootfs。

在 openEuler/Yocto 下模块会被打成 RPM 包，路径类似：

```
tmp/deploy/rpm/aarch64/
  kernel-modules-<内核版本>-*.aarch64.rpm        # 打包好的“全量模块”集合
  kernel-module-<驱动名>-<内核版本>-*.aarch64.rpm # 单个驱动拆包
```

要让它们进 rootfs，有三种常用方式：

1. 镜像里装“全部模块”

```text
# conf/local.conf 或你的镜像配方里：
IMAGE_INSTALL:append = " kernel-modules"
```

2. 只装所需驱动（更省空间）

```text
IMAGE_INSTALL:append = " kernel-module-xhci-hcd kernel-module-usbnet kernel-module-igb"
```

3. 已经烧好的系统上手动安装

```bash
# 把上面 deploy/rpm/aarch64/ 下的包拷到板子
rpm -ivh kernel-module-xxx-*.aarch64.rpm
depmod -a
```

验证与定位：

* 构建完镜像后，在构建机临时根目录可看到：
  `tmp/work/.../<image>/image/lib/modules/<uname-r>/`
* 目标机上看：
  `uname -r` 与 `/lib/modules/<uname-r>/` 是否匹配；`modinfo <模块名>`、`lsmod`。

开机自动加载：

* 最稳的是在镜像里放一个文件 `/etc/modules-load.d/xxx.conf`，写上需要自启动的模块名；或者写一个很小的配方/追加到 rootfs
  去投放该文件。

模块最终应当位于目标机的 `/lib/modules/<uname -r>/`，但是否“出现在根文件系统里”，取决于你是否把相关 **模块包** 安装进镜像（或事后用
rpm 安装）。添加 `IMAGE_INSTALL` 是最直接的做法。

#### 8.4.1 infiniband 模块

在前面我们添加 `fragment-infiniband.cfg` 之后会构建出 `INFINIBAND` 相关的内核模块：

打包进 `rootfs`:

```text
cd ~/phytium_build/conf
```

```text
vim local.conf
```

增加以下行：

```text
IMAGE_INSTALL:append = " kernel-modules"
```

> 在目标板启动操作系统之后，可以到目录
> ```text
> cd /lib/modules/5.10.0-openeuler
> ``` 
> 查看

### 8.5 修改内核源码

与设备树修改的过程一致，注意不能直接修改源码，需要生成补丁，然后将补丁放到配方指定的位置。

## 9. 版本管理问题

构建稳定可复现的版本一定要仔细记录修改点

### 9.1 使用 Git 跟踪构建配置和源码修改

内核的修改 commit message 记录在这个目录

```text
cd ~/openeuler/workdir/build/phytium/tmp/work-shared/phytium/kernel-source
git log
```

### 9.2 内核配置项

内核配置项使用 `~/phytium_build/fragment` 下的 `fragment.cfg` 文件跟踪。

### 9.3 配方

我们修改过关于机器的配方在这个目录：

```text
cd ~/openeuler/workdir/src/yocto-meta-openeuler/bsp/meta-phytium/conf/machine/include/
vim phy-base.inc
```

在 `bbappend` 目录下的文件也使用 Git 跟踪。

## 10. 配方问题

看哪些 layer 已接入、路径在哪

```text
bitbake-layers show-layers
```

## 11. 添加gcc make 到文件系统

### 11.1 修改文件系统配置

修改文件<build>conf/local.conf 添加如下变量:

```text
IMAGE_INSTALL:append = " gcc g++ make autoconf automake gcc-symlinks g++-symlinks"
```

### 11.2 去除 GCC 限制

修改文件<work>src/yocto-meta-openeuler/meta-openeuler/conf/openeuler-ros-distro-recipe-blacklist.inc

```text
cd ~/openeuler/workdir/src/yocto-meta-openeuler/meta-openeuler/conf
```

```text
vim openeuler-ros-distro-recipe-blacklist.inc
```

注释 :  #SKIP_RECIPE[gcc] = "Not building with openEuler Embedded ros runtime."

### 11.3 解决编译安装 gcc 的错误

修改文件<work>src/yocto-meta-openeuler/meta-openeuler/recipes-devtools/gcc/gcc-target.inc

```text
do_install () {
        oe_runmake 'DESTDIR=${D}' install-host

        # Add unwind.h, it comes from libgcc which we don't want to build again
165行:  #install ${STAGING_LIBDIR_NATIVE}/${TARGET_SYS}/gcc/${TARGET_SYS}/${BINV}/include/unwind.h ${D}${libdir}/gcc/${TARGET_SYS}/${BINV}/include/
```

添加:

```text
install ${OPENEULER_NATIVESDK_SYSROOT}/usr/lib/gcc/x86_64-openeulersdk-linux/12.3.0/include/unwind.h  ${D}${libdir}/gcc/${TARGET_SYS}/${BINV}/include/
```

### 11.4 文件系统生成

重新编译文件系统，其中就包括 `gcc g++ make autoconf automake gcc-symlinks` 这些工具了。

```text
bitbake openeuler-image
```

### 11.5 开发板上编译应用

开发板上编译应用，需要设置如下环境变量

```text
export LIBRARY_PATH=/lib64/gcc/aarch64-openeuler-linux-gnu/12.3.1:$LIBRARY_PATH
```


