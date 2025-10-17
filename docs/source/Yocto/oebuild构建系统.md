# oebuild 构建系统

## 1. 创建独立的 python 虚拟环境

在 Ubuntu 24.04 中

创建工程目录

```text
mkdir -p ~/openEuler
```

```text
sudo apt update
sudo apt install -y python3-venv python3-full build-essential
```

建立虚拟环境

```text
python3 -m venv ~/venvs/oebuild
source ~/venvs/oebuild/bin/activate
```

升级 pip 并安装

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
cd ~/openEuler
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

验证

```text
docker run --rm hello-world
```

## 3. 运行 oebuild

初始化工作目录

```text
oebuild init -b openEuler-24.03-LTS workdir
cd /home/wuyuhang/openEuler/workdir
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

### 5.1 增大 swap 区，如果 wsl 内存够大可以跳过

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
cd /home/wuyuhang/openEuler/workdir
oebuild generate -p phytium
```

```text
cd /home/wuyuhang/openEuler/workdir/build/phytium
oebuild bitbake openeuler-image
```

### 5.3 编译 binutils 出现 gold 链接问题

这版 binutils 把 dwp 放在 gold 目录下。某些组合下它会被错误地用 ld.bfd 去链接并把 libgold.a 拉进来，但缺少 gold
需要的其它对象/顺序/配置，导致这些 gold:: 符号解析失败。常见修法是禁用 gold（连带 dwp），或者让目标侧 libstdc++ 等在那一步可用；

```text
cd /home/wuyuhang/openEuler/workdir/src/yocto-meta-openeuler/meta-openeuler/recipes-devtools/binutils
```

修改 binutils_%.bbappend 内容：

```text
# 关闭 gold（同时就不会去构建 gold 目录下的 dwp）
PACKAGECONFIG:remove = " gold"
EXTRA_OECONF:append = " --disable-gold"
```

因为是增量编译的，可以回到工作目录继续重新编译

```text
cd ~/openEuler/workdir/build/phytium
oebuild bitbake -c cleansstate binutils
oebuild bitbake openeuler-image
```

### 5.4 openssl

好的，下面把“方案 C”的最终做法整理为一份可直接执行的清单。

# 目标

稳定构建 `openssl`/`openssl-native`，避免 `do_compile`/`do_install` 并行导致的竞态与 fuzz/test 目标引发的链接异常。

# 一、在 `local.conf` 增加配置（最快）

编辑 `build/conf/local.conf`，追加如下行：

```bitbake
# 1) 禁用并行编译与并行安装（openssl 及其 native 变体）
PARALLEL_MAKE:pn-openssl = ""
PARALLEL_MAKEINST:pn-openssl = ""
PARALLEL_MAKE:pn-openssl-native = ""
PARALLEL_MAKEINST:pn-openssl-native = ""

# 2) 关闭测试与 fuzz 相关目标（生产环境不需要，减少不确定性）
EXTRA_OECONF:append:pn-openssl = " no-tests no-fuzz-afl no-fuzz-libfuzzer"
EXTRA_OECONF:append:pn-openssl-native = " no-tests no-fuzz-afl no-fuzz-libfuzzer"
```

# 二、清理并重建

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

# 三、可选：长期化（更规范，用 bbappend）

如果希望把规避策略沉淀到自定义层，创建：

```
meta-local/recipes-connectivity/openssl/openssl_%.bbappend
```

内容：

```bitbake
PARALLEL_MAKE = ""
PARALLEL_MAKEINST = ""
EXTRA_OECONF:append = " no-tests no-fuzz-afl no-fuzz-libfuzzer"
```

把 `meta-local` 加入 `bblayers.conf` 后，执行同样的清理与重建步骤。

# 四、验证要点

* 构建日志不再出现 `mv: cannot stat ...*.d.tmp`、`libcrypto.a: malformed archive`、`OPENSSL_die` 未解析等并行/竞态类错误。
* `tmp/work/.../openssl-*/image/` 下文件完整；镜像里 `openssl`/`libssl`/`libcrypto` 安装正常。

# 五、注意

* 保证构建目录在 Linux 文件系统（`/home/...`），不要放在 `/mnt/c`。
* 空间与 inode 充足（建议预留 >30GB），否则也会诱发“文件截断/损坏”类问题。

以上就是“方案 C”的完整落地版本。后续如果升级到更高版本的 OpenSSL，再视情况取消这些限制即可。


## 6. 产物

```text
cd /home/wuyuhang/openEuler/workdir/build/phytium/tmp/deploy/images/phytium
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

