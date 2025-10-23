# oebuild 构建系统

openEuler Embeddedd的核心构建系统是基于Yocto，但又根据自身的需求做了很多定制化的开发。

社区：

[飞腾 bsp](https://gitee.com/phytium_embedded/phytium-openeuler-embedded-bsp)

[Phytium CPU OpenEuler Embedded 用户使用手册]()

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

初始化工作目录

```text
oebuild init -b openEuler-24.03-LTS workdir
cd ~/openeuler/workdir
```

创建编译配置

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

```text
cd ~/openeuler/workdir
source ~/venvs/oebuild/bin/activate
oebuild generate -p phytium
```

使用 Intel 13400 16线程的 CPU 编译时间约为 45 分钟。

```text
cd ~/openeuler/workdir/build/phytium
oebuild bitbake openeuler-image
```

### 5.3 可能的编译问题

#### 5.3.1 编译 binutils 出现 gold 链接问题

这版 binutils 把 dwp 放在 gold 目录下。某些组合下它会被错误地用 ld.bfd 去链接并把 libgold.a 拉进来，但缺少 gold
需要的其它对象/顺序/配置，导致这些 gold:: 符号解析失败。常见修法是禁用 gold（连带 dwp），或者让目标侧 libstdc++ 等在那一步可用；

```text
cd ~/openeuler/workdir/src/yocto-meta-openeuler/meta-openeuler/recipes-devtools/binutils
```

修改 binutils_%.bbappend 内容：

```text
# 关闭 gold（同时就不会去构建 gold 目录下的 dwp）
PACKAGECONFIG:remove = " gold"
EXTRA_OECONF:append = " --disable-gold"
```

因为是增量编译的，可以回到工作目录继续重新编译

```text
cd ~/openeuler/workdir/build/phytium
oebuild bitbake -c cleansstate binutils
oebuild bitbake openeuler-image
```

#### 5.3.2 openssl

稳定构建 `openssl`/`openssl-native`，避免 `do_compile`/`do_install` 并行导致的竞态与 fuzz/test 目标引发的链接异常。

##### 一、在 `local.conf` 增加配置（最快）

编辑 `build/conf/local.conf`，追加如下行：

```text
# 1) 禁用并行编译与并行安装（openssl 及其 native 变体）
PARALLEL_MAKE:pn-openssl = ""
PARALLEL_MAKEINST:pn-openssl = ""
PARALLEL_MAKE:pn-openssl-native = ""
PARALLEL_MAKEINST:pn-openssl-native = ""

# 2) 关闭测试与 fuzz 相关目标（生产环境不需要，减少不确定性）
EXTRA_OECONF:append:pn-openssl = " no-tests no-fuzz-afl no-fuzz-libfuzzer"
EXTRA_OECONF:append:pn-openssl-native = " no-tests no-fuzz-afl no-fuzz-libfuzzer"
```

##### 二、清理并重建

```bash
# 进入你的 oebuild 工作目录
cd <work>

# 清理旧产物（避免复用到已损坏/不完整的缓存）
bitbake -c cleansstate openssl-native openssl

# 先单包验证，再继续整体构建
bitbake openssl-native
bitbake openssl

# 通过后继续你的镜像/目标
bitbake <your-image-or-target>
```

##### 三、可选：长期化（更规范，用 bbappend）

如果希望把规避策略沉淀到自定义层，创建：

```
meta-local/recipes-connectivity/openssl/openssl_%.bbappend
```

内容：

```text
PARALLEL_MAKE = ""
PARALLEL_MAKEINST = ""
EXTRA_OECONF:append = " no-tests no-fuzz-afl no-fuzz-libfuzzer"
```

把 `meta-local` 加入 `bblayers.conf` 后，执行同样的清理与重建步骤。

##### 四、验证要点

* 构建日志不再出现 `mv: cannot stat ...*.d.tmp`、`libcrypto.a: malformed archive`、`OPENSSL_die` 未解析等并行/竞态类错误。
* `tmp/work/.../openssl-*/image/` 下文件完整；镜像里 `openssl`/`libssl`/`libcrypto` 安装正常。

#### 5.3.3 dtc 时间戳问题

```text
source ~/venvs/oebuild/bin/activate
oebuild bitbake -c cleansstate dtc-native
oebuild bitbake dtc-native
```

#### 5.3.4 内核编译缺少依赖

##### 问题现象

* `linux-openeuler-5.10-r0 do_compile: oe_runmake failed`
* 随后在尝试补依赖时又出现：

    * `Nothing PROVIDES 'dwarves-native'`（应为 `pahole-native`）
    * `Nothing PROVIDES 'libelf-native'`（应为 `elfutils-native`）

##### 根因

1. Yocto 内核开启了 BTF（`CONFIG_DEBUG_INFO_BTF=y`），内核链接 `BTF` 需要 `pahole` 与 `libelf` 等原生工具。
2. 我们在 `local.conf` 里用错了依赖名称：

    * `dwarves-native` → 实际配方名是 `pahole-native`
    * `libelf-native` → 实际配方名是 `elfutils-native`
3. 因 provider 名称不匹配，BitBake 无法解析依赖，导致目标 `linux-openeuler` “no buildable providers”。

##### 解决方案

1. 在 `build/conf/local.conf` 正确补齐原生依赖：

```text
# 给 linux-openeuler 补齐原生依赖
DEPENDS:append:pn-linux-openeuler = " dtc-native bc-native openssl-native elfutils-native pahole-native flex-native bison-native"
```

2. 清理并重建：

```text
oebuild bitbake -c cleansstate linux-openeuler elfutils-native pahole-native
oebuild bitbake linux-openeuler
```

这套配置能稳定把 `linux-openeuler` 编过去；后续若开启更多内核特性（模块签名、LTO 等）再逐项补齐依赖或加碎片即可。

## 6. 产物

编译出 **kernel image ,rootfs ,dtb ,iso and phydisk.img**

```text
cd ~/openeuler/workdir/build/phytium/tmp/deploy/images/phytium
```

```text
wuyuhang@Tokamark-2:~/openEuler/workdir/build/phytium/tmp/deploy/images/phytium$ ll
total 1082764
drwxr-xr-x 3 wuyuhang docker      4096 Oct 17 17:53 ./
drwxr-xr-x 3 wuyuhang docker      4096 Oct 17 17:21 ../
drwxr-xr-x 3 wuyuhang docker      4096 Oct 17 17:21 EFI/
-rw-r--r-- 2 wuyuhang docker   2154496 Oct 17 17:21 grub-efi-bootaa64.efi
lrwxrwxrwx 2 wuyuhang docker        41 Oct 17 17:50 Image -> Image--5.10-r0-phytium-20251017095001.bin*
-rwxr-xr-x 2 wuyuhang docker  15028736 Oct 17 17:33 Image--5.10-r0-phytium-20251017095001.bin*
lrwxrwxrwx 2 wuyuhang docker        41 Oct 17 17:50 Image-phytium.bin -> Image--5.10-r0-phytium-20251017095001.bin*
-rw-r--r-- 2 wuyuhang docker 158070507 Oct 17 17:52 modules--5.10-r0-phytium-20251017095001.tgz
lrwxrwxrwx 2 wuyuhang docker        43 Oct 17 17:52 modules-phytium.tgz -> modules--5.10-r0-phytium-20251017095001.tgz
-rw-r--r-- 2 wuyuhang docker  20780893 Oct 17 17:52 openeuler-image-live-phytium-20251017095001.rootfs.cpio.gz
-rw-r--r-- 2 wuyuhang docker     10116 Oct 17 17:52 openeuler-image-live-phytium-20251017095001.rootfs.manifest
-rw-r--r-- 2 wuyuhang docker    351031 Oct 17 17:52 openeuler-image-live-phytium-20251017095001.testdata.json
lrwxrwxrwx 2 wuyuhang docker        58 Oct 17 17:52 openeuler-image-live-phytium.cpio.gz -> openeuler-image-live-phytium-20251017095001.rootfs.cpio.gz
lrwxrwxrwx 2 wuyuhang docker        59 Oct 17 17:52 openeuler-image-live-phytium.manifest -> openeuler-image-live-phytium-20251017095001.rootfs.manifest
lrwxrwxrwx 2 wuyuhang docker        57 Oct 17 17:52 openeuler-image-live-phytium.testdata.json -> openeuler-image-live-phytium-20251017095001.testdata.json
-rw-r--r-- 2 wuyuhang docker 398608384 Oct 17 17:53 openeuler-image-phytium-20251017095001.iso
-rw-r--r-- 2 wuyuhang docker 321165312 Oct 17 17:53 openeuler-image-phytium-20251017095001.rootfs.ext4
-rw-r--r-- 2 wuyuhang docker     25072 Oct 17 17:53 openeuler-image-phytium-20251017095001.rootfs.manifest
-rw-r--r-- 2 wuyuhang docker  69651439 Oct 17 17:53 openeuler-image-phytium-20251017095001.rootfs.tar.bz2
-rw-r--r-- 2 wuyuhang docker    349380 Oct 17 17:53 openeuler-image-phytium-20251017095001.testdata.json
lrwxrwxrwx 2 wuyuhang docker        50 Oct 17 17:53 openeuler-image-phytium.ext4 -> openeuler-image-phytium-20251017095001.rootfs.ext4
lrwxrwxrwx 2 wuyuhang docker        42 Oct 17 17:53 openeuler-image-phytium.iso -> openeuler-image-phytium-20251017095001.iso
lrwxrwxrwx 2 wuyuhang docker        54 Oct 17 17:53 openeuler-image-phytium.manifest -> openeuler-image-phytium-20251017095001.rootfs.manifest
lrwxrwxrwx 2 wuyuhang docker        53 Oct 17 17:53 openeuler-image-phytium.tar.bz2 -> openeuler-image-phytium-20251017095001.rootfs.tar.bz2
lrwxrwxrwx 2 wuyuhang docker        52 Oct 17 17:53 openeuler-image-phytium.testdata.json -> openeuler-image-phytium-20251017095001.testdata.json
-rw-r--r-- 2 wuyuhang docker     21961 Oct 17 17:52 pe2201-demo-ddr4--5.10-r0-phytium-20251017095001.dtb
lrwxrwxrwx 2 wuyuhang docker        52 Oct 17 17:52 pe2201-demo-ddr4.dtb -> pe2201-demo-ddr4--5.10-r0-phytium-20251017095001.dtb
lrwxrwxrwx 2 wuyuhang docker        52 Oct 17 17:52 pe2201-demo-ddr4-phytium.dtb -> pe2201-demo-ddr4--5.10-r0-phytium-20251017095001.dtb
-rw-r--r-- 2 wuyuhang docker     22785 Oct 17 17:52 pe2202-demo-ddr4--5.10-r0-phytium-20251017095001.dtb
lrwxrwxrwx 2 wuyuhang docker        52 Oct 17 17:52 pe2202-demo-ddr4.dtb -> pe2202-demo-ddr4--5.10-r0-phytium-20251017095001.dtb
lrwxrwxrwx 2 wuyuhang docker        52 Oct 17 17:52 pe2202-demo-ddr4-phytium.dtb -> pe2202-demo-ddr4--5.10-r0-phytium-20251017095001.dtb
-rw-r--r-- 2 wuyuhang docker     23412 Oct 17 17:52 pe2204-demo-ddr4--5.10-r0-phytium-20251017095001.dtb
lrwxrwxrwx 2 wuyuhang docker        52 Oct 17 17:52 pe2204-demo-ddr4.dtb -> pe2204-demo-ddr4--5.10-r0-phytium-20251017095001.dtb
lrwxrwxrwx 2 wuyuhang docker        52 Oct 17 17:52 pe2204-demo-ddr4-phytium.dtb -> pe2204-demo-ddr4--5.10-r0-phytium-20251017095001.dtb
-rw-r--r-- 2 wuyuhang docker     24639 Oct 17 17:52 phytiumpi_firefly--5.10-r0-phytium-20251017095001.dtb
lrwxrwxrwx 2 wuyuhang docker        53 Oct 17 17:52 phytiumpi_firefly.dtb -> phytiumpi_firefly--5.10-r0-phytium-20251017095001.dtb
lrwxrwxrwx 2 wuyuhang docker        53 Oct 17 17:52 phytiumpi_firefly-phytium.dtb -> phytiumpi_firefly--5.10-r0-phytium-20251017095001.dtb
-rwxr-xr-x 2 wuyuhang docker 206689256 Oct 17 17:33 vmlinux*
```

## 7. 定制设备树

上面的构建流程使用的源码来自 oebuild 和 phytium bsp，为了支持我们的 target-board，我们需要编译自己的设备树。

这是 phytium
提供的修改设备树的[方法](https://gitee.com/phytium_embedded/phytium-openeuler-embedded-bsp/wikis/%E5%A6%82%E4%BD%95%E4%BF%AE%E6%94%B9%E7%BC%96%E8%AF%91%E8%AE%BE%E5%A4%87%E6%A0%91)

### 7.1 先进入 Linux 内核源码目录

```text
cd ~/openeuler/workdir/build/phytium/tmp/work-shared/phytium/kernel-source
```

设备树放在 arch 子目录下

```text
cd arch/arm64/boot/dts/phytium/
```

### 7.2 新增和修改设备树

D2000 CPU 使用pd2008前缀的dtb文件。

将设备树文件复制到源码的设备树目录下完成设备树的**新增**：

```text
cp -v ~/device-tree/pd2008-generic-psci-soc.dtsi ./
cp -v ~/device-tree/pd2008-devboard-dsk.dts ./
```

如果要修改设备树的内容，
例如添加节点, 修改文件 `arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dts`

### 7.3 修改 Makefile

增加的文件要编译需要修改这个目录下的 Makefile，添加新增的设备树文件名

```text
vim Makefile
```

```text
## d2000 dev board:
dtb-$(CONFIG_ARCH_PHYTIUM) += pd2008-devboard-dsk.dtb
```

### 7.4 修改编译配方

```text
vim ~/openeuler/workdir/src/yocto-meta-openeuler/bsp/meta-phytium/conf/machine/include/phy-base.inc
```

在 `KERNEL_DEVICETREE` 字段增加我们的新设备树

```text
KERNEL_DEVICETREE ??= " \
    phytium/pe2202-demo-ddr4.dtb \
    phytium/pe2201-demo-ddr4.dtb \
    phytium/pe2204-demo-ddr4.dtb \
    phytium/phytiumpi_firefly.dtb \
    phytium/pd2008-devboard-dsk.dtb \
    "
```

### 7.5 生成补丁

回到源码目录

```text
cd ~/openeuler/workdir/build/phytium/tmp/work-shared/phytium/kernel-source
```

生成设备树补丁

```text
git add .
git commit -s -m "update dts"
git format-patch -1
```

**0001-update-d2000-dtb.patch**

### 7.6 修改内核构建配方

将补丁放到构建系统的 src 子目录中

```text
cp -v 0001-update-d2000-dtb.patch ~/openeuler/workdir/src/yocto-meta-openeuler/bsp/meta-phytium/recipes-kernel/linux/files/
```

进入配方所在目录并修改配方

```text
cd ~/openeuler/workdir/src/yocto-meta-openeuler/bsp/meta-phytium/recipes-kernel/linux/
```

`vim linux-openeuler.bb`

加入以下内容

```text
SRC_URI:append = "\
file://0001-update-d2000-dtb.patch \
"
```

### 7.7 重新编译内核

```text
source ~/venvs/oebuild/bin/activate
cd ~/openeuler/workdir/build/phytium
```

```text
oebuild bitbake linux-openeuler -c clean
oebuild bitbake linux-openeuler
```



