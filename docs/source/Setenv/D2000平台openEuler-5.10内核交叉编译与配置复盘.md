# D2000 平台 openEuler-5.10 内核交叉编译与配置复盘

> 目标：  
> 在 x86 WSL Ubuntu 上，基于 openEuler 22.03 LTS SP4 提取的 5.10.0-216 内核源码，
> 引入飞腾 D2000 BSP + 自己的 `pd2008` 设备树，合并服务器 `.config`，
> 得到一套可以在 D2000 板子上运行的内核 Image / DTB / 模块。

---

## 1. 环境说明

- 主机环境：Windows 11 + WSL2 Ubuntu 24.04
- 目标架构：aarch64 (ARM64)
- 交叉工具链安装：

```bash
sudo apt update

# 交叉编译工具链
sudo apt install \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    binutils-aarch64-linux-gnu

# 内核编译依赖
sudo apt install \
    make bc bison flex \
    libssl-dev libelf-dev \
    libncurses-dev \
    dwarves
````

统一使用的环境变量：

```bash
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
```

---

## 2. 准备源码与 BSP 文件

### 2.1 从 ISO 提取内核源码

从 `openEuler-22.03-LTS-SP4-everything-aarch64-dvd.iso` 里提取到的源码包：

* `openEuler-5.10.0-216-src.tar.xz`

在 `$HOME` 下准备临时工作目录：

```bash
cd ~
mkdir tmp-2
cd tmp-2
cp ../openEuler-5.10.0-216-src.tar.xz .
tar -xf openEuler-5.10.0-216-src.tar.xz
cd openEuler-5.10.0-216-src
```

此时目录结构类似：

```text
~/tmp-2/openEuler-5.10.0-216-src/
    arch/
    drivers/
    ...
    Makefile
```

### 2.2 拷贝飞腾 BSP 相关文件

从 Yocto BSP 目录 `meta-phytium/recipes-kernel/linux/files/` 中拷贝到 `$HOME`：

* `0001-openeuler-phytium-opensource-v2_3.patch`
* `config/phytium_defconfig`
* 另外还有飞腾自带的诸多 DTS/DTSI、Kconfig 和驱动，已经包含在补丁里。

拷贝到内核源码中方便使用：

```bash
cd ~/tmp-2/openEuler-5.10.0-216-src
cp ~/0001-openeuler-phytium-opensource-v2_3.patch .
cp ~/phytium_defconfig arch/arm64/configs/phytium_defconfig
```

---

## 3. 在干净内核上应用飞腾 BSP 补丁

```bash
cd ~/tmp-2/openEuler-5.10.0-216-src
patch -p1 < 0001-openeuler-phytium-opensource-v2_3.patch
```

注意点：

* `.gitignore` 相关的 hunk 会提示找不到文件，可以直接 `y` 跳过；
* 关键是确认没有出现 `.rej` 文件：

```bash
find . -name '*.rej'
# 无输出即说明核心补丁均成功
```

补丁生效的验证：

```bash
ls arch/arm64/boot/dts/phytium
ls arch/arm64/configs | grep phytium
ls drivers/net/ethernet/phytium
```

能看到诸如 `pe2204-*.dts`、`phytium_defconfig` 等文件即表明 BSP 已经接入。

---

## 4. 集成自定义 pd2008 设备树

已有两个自定义 DTS 文件放在 `$HOME`：

* `pd2008-devboard-dsk.dts`
* `pd2008-generic-psci-soc.dtsi`

### 4.1 拷贝到 Phytium DTS 目录

```bash
cd ~/tmp-2/openEuler-5.10.0-216-src
cp ~/pd2008-devboard-dsk.dts      arch/arm64/boot/dts/phytium/
cp ~/pd2008-generic-psci-soc.dtsi arch/arm64/boot/dts/phytium/
```

确保 DTS 顶部 include 路径正确，例如：

```dts
/dts-v1/;

/include/ "pd2008-generic-psci-soc.dtsi"
```

### 4.2 在 Makefile 中注册 pd2008 DTB

编辑 `arch/arm64/boot/dts/phytium/Makefile`，在其他 `dtb-$(...) += xxx.dtb` 后追加一行：

```make
dtb-$(CONFIG_ARCH_PHYTIUM) += pd2008-devboard-dsk.dtb
```

（左侧条件保持和现有 Phytium 条目一致，如为 `CONFIG_ARCH_PHYTIUM_D2000` 就对应修改。）

---

## 5. 使用 phytium_defconfig 做基础交叉编译验证

这一阶段只验证「BSP + DTS + 工具链」是否可编译通过，不合并发行版配置。

### 5.1 生成配置并编译

```bash
cd ~/tmp-2/openEuler-5.10.0-216-src

export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-

make mrproper           # 可选，保证干净
make phytium_defconfig  # 使用飞腾的板级 defconfig

# 编译内核镜像 + DTB + 模块
make -j"$(nproc)" Image dtbs modules

# 安装模块到临时根目录
mkdir -p ~/tmp-2/rootfs-phytium
make modules_install INSTALL_MOD_PATH=~/tmp-2/rootfs-phytium
```

确认产物：

```bash
ls -lh arch/arm64/boot/Image
ls arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb
ls ~/tmp-2/rootfs-phytium/lib/modules
```

这一步说明：

* BSP 补丁无冲突；
* 自定义 `pd2008` 设备树可以正常参与编译。

---

## 6. 合并服务器 .config 与 phytium_defconfig

目标：在保持 openEuler 服务器功能的前提下，加入 Phytium 板级支持。

### 6.1 准备服务器配置

从正在运行的 openEuler 服务器系统上拷贝 `/boot/config-5.10.0-216.*` 到 WSL，例如：

```bash
cp /path/to/server/config-5.10.0-216.xxx ~/tmp-2/openEuler-5.10.0-216-src/.config.server
```

进入源码目录：

```bash
cd ~/tmp-2/openEuler-5.10.0-216-src
```

### 6.2 使用 merge_config.sh 合并

```bash
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-

./scripts/kconfig/merge_config.sh -m .config.server \
    arch/arm64/configs/phytium_defconfig

mv .config .config.merged
cp .config.merged .config

# 让新选项补全默认值
make olddefconfig
```

此时 `.config` 即为「服务器配置 + Phytium 板级配置」的合并结果。

---

## 7. 合并后编译问题与修改记录

合并后第一次编译会遇到多处与厂商扩展代码相关的错误。下面记录逐个处理方式。

### 7.1 关闭 Phytium 显示控制器 DRM 驱动

报错类型：`drivers/gpu/drm/phytium/phytium_pci.c` 中
`phytium_kick_out_firmware_fb()` 只有调用点，没有定义。

处理策略：当前 D2000 用于 server，不需要图形输出，直接关闭该 DRM 驱动。

操作方法（推荐用 menuconfig）：

```bash
make menuconfig
```

路径：

* `Device Drivers`

    * `Graphics support`

        * 搜索含 “Phytium” 的条目（例如 “Phytium display controller” 等），全部设为 `N`。

保存退出后：

```bash
make olddefconfig
```

之后重新编译，DRM Phytium 目录不再参与构建。

> 说明：如果日后需要使用显示输出，可以再从飞腾 Yocto 原始内核中把缺失的函数实现补回来，然后重新打开该选项。

---

### 7.2 关闭 sdma-dae 模块（IOMMU SVA 相关缺失）

报错文件：`drivers/misc/sdma-dae/sdma_cdev.c`

典型错误：

* `implicit declaration of function 'iommu_sva_bind_device'`
* `IOMMU_PASID_INVALID undeclared`

说明 sdma-dae 模块依赖的 IOMMU SVA 接口在当前 5.10 内核里没有实现，
而我们暂时不需要这个调试/加速模块。

处理方法：关闭 sdma-dae 相关配置。

操作（任选其一）：

1）`scripts/config` 方式（实际符号视 Kconfig 为准）：

```bash
./scripts/config -d CONFIG_SDMA_DAE
make olddefconfig
```

2）`menuconfig` 方式：

```bash
make menuconfig
```

在搜索界面 `/` 中搜索 `sdma-dae` 或关键字，找到对应选项并关闭（设为 `N`），保存后 `make olddefconfig`。

---

### 7.3 关闭 KVM 及虚拟化（SVE KVM 补丁不完整）

报错文件：`arch/arm64/kvm/reset.c`

错误示例：

```c
kvm_sve_max_vl = sve_max_virtualisable_vl();
                         ^~~~~~~~~~~~~~~~~~~
error: implicit declaration of function ‘sve_max_virtualisable_vl’
```

说明 KVM SVE 的增强补丁在当前树中不完整，缺少 `sve_max_virtualisable_vl()` 的实现。
当前阶段 D2000 上不需要运行 KVM 虚拟机，可以直接关闭 KVM 和虚拟化。

关闭方式：

```bash
./scripts/config -d CONFIG_KVM
./scripts/config -d CONFIG_VIRTUALIZATION
make olddefconfig
```

如有 ARM 特定 KVM 选项（`CONFIG_KVM_ARM_HOST` 等），也一并关闭。

---

### 7.4 处理 HISILICON_IRQ_MBIGEN 与 vtimer_irqbypass 链接错误

报错发生在链接最终 `vmlinux` 时：

```text
aarch64-linux-gnu-ld: drivers/irqchip/irq-mbigen.o: in function `vtimer_mbigen_device_probe':
irq-mbigen.c: undefined reference to `vtimer_irqbypass'
...
```

分析：

* `drivers/irqchip/irq-mbigen.c` 中有：

  ```c
  extern bool vtimer_irqbypass;
  ```

* 真正的定义在 `arch/arm64/kvm/arch_timer.c` 中，但它只在 `CONFIG_KVM=y` 时编译；

* 前一步我们已经关闭了 KVM → 链接时只剩下 `irq-mbigen.o` 在引用该符号，导致 undefined reference；

* 通过 `scripts/config -d CONFIG_HISILICON_IRQ_MBIGEN` 试图关闭该驱动，但 `make olddefconfig` 会因为某些 `select`
  语句再次自动打开它，导致无法从 Kconfig 层面彻底关掉。

最终处理策略：在 `irq-mbigen.c` 内部为 `vtimer_irqbypass` 提供一个 dummy 变量，在 KVM 关闭的情况下禁用该优化功能，同时避免链接错误。

#### 7.4.1 修改 irq-mbigen.c

编辑 `drivers/irqchip/irq-mbigen.c`，找到原来的声明：

```c
extern bool vtimer_irqbypass;
```

替换为：

```c
#if IS_ENABLED(CONFIG_KVM)
extern bool vtimer_irqbypass;
#else
/*
 * KVM 关闭时，这个驱动仍然会编译。
 * 这里提供一个仅在本文件可见的 dummy 变量，避免链接期找不到符号。
 * 默认 false，相当于关闭 vtimer irqbypass 功能。
 */
static bool vtimer_irqbypass;
#endif
```

保存后增量测试：

```bash
make drivers/irqchip/irq-mbigen.o
```

无错误后，再完整编译：

```bash
make -j"$(nproc)" Image dtbs modules
```

这一步之后：

* `vmlinux` 能够成功链接；
* BTF 相关步骤（`BTF .btf.vmlinux.bin.o` 等）也可以正常完成。

---

## 8. 最终结果与交付物

最终成功构建出的关键文件：

* 内核镜像

  ```bash
  arch/arm64/boot/Image
  ```

* 板级设备树

  ```bash
  arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb
  ```

* 模块安装目录（合并配置版本）

  ```bash
  ~/tmp-2/rootfs-merged/lib/modules/5.10.0-216-*
  ```

这些文件可以通过 scp 拷贝到 D2000 板子上，配合 U-Boot 或 GRUB 进行启动测试。

---

## 9. 实习生复现实验的建议流程（简要版）

1. 在自己的 WSL Ubuntu 创建 `~/tmp-2`，把以下文件放到 `$HOME` 或指定目录：

    * `openEuler-5.10.0-216-src.tar.xz`
    * `0001-openeuler-phytium-opensource-v2_3.patch`
    * `phytium_defconfig`
    * `pd2008-devboard-dsk.dts`
    * `pd2008-generic-psci-soc.dtsi`
    * 服务器上导出的 `.config.server`

2. 按本文档第 2~4 节操作：解压源码、应用 BSP 补丁、接入 pd2008 DTS。

3. 按第 5 节先用 `phytium_defconfig` 编一次基础内核，确认工具链和 DTS OK。

4. 按第 6 节使用 `merge_config.sh` 合并 `.config.server` 和 `phytium_defconfig`，生成 `.config` 并 `make olddefconfig`。

5. 按第 7 节依次做配置和代码修改：

    * 关闭 Phytium DRM 显示驱动；
    * 关闭 sdma-dae 模块；
    * 关闭 KVM / 虚拟化；
    * 修改 `drivers/irqchip/irq-mbigen.c`，为 `vtimer_irqbypass` 加条件声明和 dummy 变量。

6. 再次执行：

   ```bash
   make -j$(nproc) Image dtbs modules
   make modules_install INSTALL_MOD_PATH=~/tmp-2/rootfs-merged
   ```

7. 最终确认 `Image`、`pd2008-devboard-dsk.dtb` 和模块目录均生成成功，即为复现完成。

