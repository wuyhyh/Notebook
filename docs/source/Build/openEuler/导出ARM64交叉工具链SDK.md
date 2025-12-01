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
   cd ~/oebuild/xxx-build-dir    # 你的 build 目录
   source ./envsetup.sh          # 或 oebuild 自带的环境脚本
   ```

2. 使用你实际在板子上跑的镜像名生成 SDK，典型命令类似：

   ```bash
   bitbake openeuler-image -c populate_sdk
   # 或 bitbake phytium-image -c populate_sdk
   # 镜像名称按你工程实际为准
   ```

3. 生成完成后，在下面找到 SDK 安装脚本：

   ```bash
   ls tmp/deploy/sdk/
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
scp tmp/deploy/sdk/openeuler-glibc-x86_64-openeuler-image-armv8a-phytium-toolchain-24.03-LTS.sh \
    user@wsl-host:~/phytium-sdk/
```

也可以先拷到 Windows，再通过共享目录拖进 WSL，对流程无影响。

---

## 3. 在目标主机上安装交叉工具链 SDK

### 3.1 建议安装到用户目录（推荐做法）

在 WSL 的 shell 中：

```bash
cd ~/phytium-sdk
chmod +x openeuler-glibc-x86_64-openeuler-image-armv8a-phytium-toolchain-24.03-LTS.sh

# 安装到用户目录下，无需 sudo
./openeuler-glibc-x86_64-openeuler-image-armv8a-phytium-toolchain-24.03-LTS.sh \
    -d $HOME/phytium-sdk/sdk-24.03 -y
```

安装完成后目录结构大致如下：

```bash
ls $HOME/phytium-sdk/sdk-24.03
# environment-setup-armv8a-openeuler-linux
# site-config-armv8a-openeuler-linux
# sysroots/
# ...
```

这一套就是可移植的交叉编译工具链。

### 3.2 如果安装到 /opt（不推荐，但可以）

如果你坚持用 `/opt/phytium-sdk`：

```bash
sudo ./openeuler-...-toolchain-24.03-LTS.sh -d /opt/phytium-sdk -y

# 装完务必把目录权限改成你自己的，否则后续会一堆 Permission denied：
sudo chown -R $USER:$USER /opt/phytium-sdk
```

否则后面 `source environment-setup-...` 或编内核时，会因为目录只读导致各种 `mkdir: Permission denied`、`fixdep` 写不了文件的问题。

---

## 4. 使用 environment-setup 脚本配置交叉编译环境

每次要用这套工具链前，在 shell 里执行：

```bash
# 根据你安装路径选择其一：
source $HOME/phytium-sdk/sdk-24.03/environment-setup-armv8a-openeuler-linux
# 或
# source /opt/phytium-sdk/environment-setup-armv8a-openeuler-linux
```

然后检查几个关键变量：

```bash
echo "$CC"            # 预期：armv8a-openeuler-linux-gcc
echo "$CROSS_COMPILE" # 预期：armv8a-openeuler-linux-
armv8a-openeuler-linux-gcc -v
```

如果 `source` 时没有大量报错，且上述命令输出正常，就说明工具链环境已经就绪。

注意：

* `source` 这一步只做“设置环境变量”，理论上不应该疯狂打印错误；
* 如果有大量 Permission denied，多半是安装目录或你当前工作目录里有 root 拥有的文件，需要 `chown` 修正。

---

## 5. 在这套工具链环境中编译内核（简要示例）

后续在同一个 shell 中：

1. 确保内核源码目录属于你这个用户（不是 root）：

   ```bash
   sudo chown -R $USER:$USER ~/tmp-2/openEuler-5.10.0-216-src
   ```

2. 使用 merge 的 `.config`：

   ```bash
   cd ~/tmp-2/openEuler-5.10.0-216-src

   cp ~/path/to/merge-config .config
   make ARCH=arm64 olddefconfig
   ```

3. 编译内核 / 模块 / 设备树：

   ```bash
   make -j"$(nproc)" \
        ARCH=arm64 \
        CROSS_COMPILE="$CROSS_COMPILE" \
        Image modules dtbs
   ```

4. 安装模块到你的 server 根文件系统（例如挂在 `~/euler/oe-root`）：

   ```bash
   make ARCH=arm64 CROSS_COMPILE="$CROSS_COMPILE" \
        INSTALL_MOD_PATH=~/euler/oe-root \
        modules_install
   ```

5. 把 `arch/arm64/boot/Image` 和对应 `dtb` 拷到目标板 NVMe 的 `/boot`，配合你现有的 U-Boot 启动流程使用。

---

## 6. 容易犯的几个错误（明确写给实习生的）

1. 误用 `/opt/buildtools/nativesdk` 下的 gcc

    * 这是宿主 buildtools，不是 ARM64 交叉工具链，编不出板子能跑的程序。

2. 用 root 安装 SDK，然后用普通用户编译

    * 结果：`source environment-setup` 和 `make` 时疯狂 Permission denied。
    * 解决：要么安装在 `$HOME`，要么 `chown -R` 给当前用户。

3. 在内核源码目录里掺杂 root 生成的中间文件

    * 结果：`fixdep`、`autoconf.h` 等都写不进去。
    * 解决：整个源码目录 `sudo chown -R $USER:$USER`，以后不要用 sudo 编内核。

---

整体流程一句话概括：

> 在 oebuild 里用 `bitbake xxx -c populate_sdk` 生成目标 SDK → 把 `.sh` 安装脚本拷到 WSL → 在用户可写目录安装 → 每次
`source environment-setup-armv8a-openeuler-linux` 后，用 `CROSS_COMPILE` 编译服务器内核 + Phytium 补丁。

如果你后面要，我可以在这个总结的基础上再写一个完整的 `extract_toolchain_and_build_kernel.sh` 脚本，把所有命令串成一键流程。
