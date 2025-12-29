# 导出 ARM64 交叉工具链 SDK

## 0. 目标与前提

目标：
从 oebuild/Yocto 工程里，**正规导出一套 ARM64 交叉工具链 SDK**，拿到 WSL（或其他 x86_64 主机）上使用，用来编译：

* openEuler 22.03/24.03 服务器内核源码
* 打上 Phytium 补丁
* 使用你 merge 好的 `.config`

前提：

* 你已经有一个可用的 oebuild/Yocto 构建工程，可以正常 `bitbake` 出镜像。
* 构建机是 x86_64 Linux（物理机/虚拟机均可）。

---

## 1. 在 oebuild 环境中生成交叉工具链 SDK

1. 进入你的 oebuild 构建目录，并加载环境（按你平时的方式）：

   ```bash
   cd ~/openeuler/workdir/build/phytium    # 你的 build 目录
   source source ~/venvs/oebuild/bin/activate          # 或 oebuild 自带的环境脚本
   ```

2. 使用你实际在板子上跑的镜像名生成 SDK，典型命令类似：

   ```bash
   bitbake openeuler-image -c populate_sdk
   # 或 bitbake phytium-image -c populate_sdk
   # 镜像名称按你工程实际为准
   ```

3. 生成完成后，在下面找到 SDK 安装脚本：

   ```bash
   ls ~/openeuler/workdir/build/phytium/tmp/deploy/sdk
   # 例：openeuler-glibc-x86_64-openeuler-image-armv8a-phytium-toolchain-24.03-LTS.sh
   ```

注意：

* 这是**目标工具链 SDK**（带 `armv8a` / `aarch64` 的那个），
  不要用 `/opt/buildtools/nativesdk/...` 里面的宿主 buildtools，那是 x86_64→x86_64 的工具链。

---

## 2. 将 SDK 安装脚本拷贝到目标主机（如 WSL）

假设要拷贝到 WSL 上：

```bash
# 在构建机上
mkdir -p $HOME/toolchains/phytium-24.03 $HOME/toolchains/phytium-sdk
cd ~/openeuler/workdir/build/phytium/tmp/deploy/sdk
cp -v openeuler-glibc-x86_64-openeuler-image-armv8a-phytium-toolchain-24.03-LTS.sh \
    $HOME/toolchains/phytium-sdk
```

---

## 3. 在目标主机上安装交叉工具链 SDK

在 WSL 的 shell 中：

```bash
cd $HOME/toolchains/phytium-sdk
chmod +x openeuler-glibc-x86_64-openeuler-image-armv8a-phytium-toolchain-24.03-LTS.sh
```

安装到用户目录下，无需 sudo

```text
./openeuler-glibc-x86_64-openeuler-image-armv8a-phytium-toolchain-24.03-LTS.sh \
    -d $HOME/toolchains/phytium-24.03 -y
```

安装完成后目录结构大致如下：

```bash
ls $HOME/toolchains/phytium-24.03
# environment-setup-armv8a-openeuler-linux
# site-config-armv8a-openeuler-linux
# sysroots/
# version-armv8a-openeuler-linux
```

这一套就是可移植的交叉编译工具链。
