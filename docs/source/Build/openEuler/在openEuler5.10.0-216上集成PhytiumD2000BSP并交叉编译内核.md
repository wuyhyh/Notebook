# 在 openEuler 5.10.0-216 上集成 Phytium D2000 BSP 并交叉编译内核

> 目标：在 x86 + WSL Ubuntu 的环境中，对 `openEuler-5.10.0-216` 内核源码应用 Phytium D2000 BSP 补丁，集成 `pd2008` 设备树，并在合并服务器 `.config` 后成功交叉编译 `Image` + `dtb` + 模块。

---

## 0. 环境准备

- Host：WSL Ubuntu 24.04（x86_64）
- 交叉工具链：

```bash
sudo apt update
sudo apt install \
    gcc-aarch64-linux-gnu g++-aarch64-linux-gnu \
    binutils-aarch64-linux-gnu \
    make bc bison flex \
    libssl-dev libelf-dev libncurses-dev \
    dwarves
````

* 关键文件（放在 `$HOME`）：

```text
openEuler-5.10.0-216-src.tar.xz          # 从 openEuler 2203 Server ISO 提取的内核源码
0001-openeuler-phytium-opensource-v2_3.patch
phytium_defconfig                         # Yocto BSP 中的 phytium_defconfig
pd2008-devboard-dsk.dts
pd2008-generic-psci-soc.dtsi
.config.server                            # 从实际运行的 openEuler 服务器上拷下来的 .config
```

---

## 1. 解包 openEuler 内核源码

```bash
mkdir -p ~/tmp-2
cd ~/tmp-2

cp ~/openEuler-5.10.0-216-src.tar.xz ./
tar -xf openEuler-5.10.0-216-src.tar.xz

cd openEuler-5.10.0-216-src
```

确认内核版本：

```bash
head Makefile
# VERSION = 5
# PATCHLEVEL = 10
# SUBLEVEL = 0
# OPENEuler_LTS = 1
# OPENEULER_MAJOR = 2203
# ...
```

---

## 2. 应用 Phytium BSP 补丁

```bash
cd ~/tmp-2/openEuler-5.10.0-216-src

cp ~/0001-openeuler-phytium-opensource-v2_3.patch .

patch -p1 < 0001-openeuler-phytium-opensource-v2_3.patch
```

说明：

* `.gitignore` 的那一个 hunk 会被跳过（源码包没有 .gitignore），可以忽略。
* 关键检查：

```bash
ls arch/arm64/boot/dts/phytium
ls arch/arm64/configs | grep phytium
ls drivers/net/ethernet/phytium
```

若以上目录/文件存在，说明 BSP 已基本应用成功。

---

## 3. 集成 pd2008 设备树

把自己的开发板 DTS/DTSI 接到 BSP tree 里：

```bash
cd ~/tmp-2/openEuler-5.10.0-216-src

cp ~/pd2008-devboard-dsk.dts      arch/arm64/boot/dts/phytium/
cp ~/pd2008-generic-psci-soc.dtsi arch/arm64/boot/dts/phytium/
```

确保 `pd2008-devboard-dsk.dts` 顶部 include 正确，例如：

```dts
/dts-v1/;
/include/ "pd2008-generic-psci-soc.dtsi"
```

修改 `arch/arm64/boot/dts/phytium/Makefile`，加入新 dtb 目标（按原文件风格）：

```make
dtb-$(CONFIG_ARCH_PHYTIUM) += pd2008-devboard-dsk.dtb
```

（如果原来是 `dtb-$(CONFIG_ARCH_PHYTIUM_D2000)`，就保持一致。）

---

## 4. 准备 phytium_defconfig 并做首次测试构建

### 4.1 拷贝 defconfig

```bash
cd ~/tmp-2/openEuler-5.10.0-216-src
cp ~/phytium_defconfig arch/arm64/configs/phytium_defconfig
```

### 4.2 使用 phytium_defconfig 生成配置

```bash
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-

make mrproper          # 第一次构建可以做，后面可选
make phytium_defconfig
```

### 4.3 关闭 Phytium DRM 显示驱动（避免编译错误）

原因：`drivers/gpu/drm/phytium/phytium_pci.c` 中使用 `phytium_kick_out_firmware_fb()`，当前代码中无定义，会导致 `implicit-function-declaration`。

直接在配置里关掉该 DRM 驱动：

```bash
./scripts/config -d CONFIG_DRM_PHYTIUM     # 实际符号名按 grep/菜单为准
make olddefconfig
```

### 4.4 首次完整构建（仅 BSP + phytium_defconfig）

```bash
make -j"$(nproc)" Image dtbs modules

mkdir -p ~/tmp-2/rootfs-test
make modules_install INSTALL_MOD_PATH=~/tmp-2/rootfs-test
```

检查：

```bash
ls arch/arm64/boot/Image
ls arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb
ls ~/tmp-2/rootfs-test/lib/modules
```

到此为止，证明：

* BSP 补丁有效
* `pd2008` DTS 能正常参与编译
* 工具链和基础配置没问题

---

## 5. 合并 openEuler 服务器配置

目标：在保留 Phytium BSP + `pd2008` 的基础上，引入服务器发行版 `.config` 中的各种功能（cgroup、容器、各种文件系统等）。

### 5.1 使用 merge_config.sh 合并

```bash
cd ~/tmp-2/openEuler-5.10.0-216-src

cp ~/config.server .config.server      # 实习生需要把实际服务器的 .config 放到这里

./scripts/kconfig/merge_config.sh -m .config.server \
    arch/arm64/configs/phytium_defconfig

mv .config .config.merged
cp .config.merged .config

make olddefconfig
```

---

## 6. 合并后遇到的问题与修复

合并 .config 后，开启了很多 BSP 中默认打开、但 openEuler 官方内核 **没有配套框架补丁** 的特性，导致编译 / 链接错误。以下是逐个关闭/修补的列表。

> 实习生照做时，只要按顺序执行这几步，就可以避免重新踩坑。

### 6.1 关闭 SDMA DAE（IOMMU SVA 相关）

错误表现（编译阶段）大致如下：

```text
drivers/misc/sdma-dae/sdma_cdev.c:57:18: error: implicit declaration of function ‘iommu_sva_bind_device’
drivers/misc/sdma-dae/sdma_cdev.c:64:17: error: implicit declaration of function ‘iommu_sva_get_pasid’
drivers/misc/sdma-dae/sdma_cdev.c:65:22: error: ‘IOMMU_PASID_INVALID’ undeclared
drivers/misc/sdma-dae/sdma_cdev.c:82:9: error: implicit declaration of function ‘iommu_sva_unbind_device’
```

原因：当前 5.10 源码没有这套 IOMMU SVA 接口，BSP 的 sdma-dae 驱动过新。

处理：直接关闭 `CONFIG_SDMA_DAE`。

```bash
./scripts/config -d CONFIG_SDMA_DAE
make olddefconfig
```

### 6.2 再次关闭 DRM Phytium

合并 `.config.server` 后，`phytium_defconfig` 中的 DRM 选项又被打开，导致之前的 `phytium_kick_out_firmware_fb` 编译错误重新出现。

处理：再次关闭 DRM Phytium：

```bash
./scripts/config -d CONFIG_DRM_PHYTIUM
make olddefconfig
```

### 6.3 关闭 KVM / 虚拟化，避免 SVE 相关错误

错误示例（编译阶段）：

```text
arch/arm64/kvm/reset.c:105:34: error: implicit declaration of function ‘sve_max_virtualisable_vl’
```

这说明 BSP 的 KVM SVE 补丁不完整（缺少 `sve_max_virtualisable_vl()` 实现），而当前内核版本没有该 helper。

现阶段 D2000 用作物理服务器，不需要 KVM 虚拟化，所以直接关闭：

```bash
./scripts/config -d CONFIG_KVM
./scripts/config -d CONFIG_VIRTUALIZATION   # 可选，视实际需要

make olddefconfig
```

### 6.4 处理 irq-mbigen 中对 vtimer_irqbypass 的依赖（链接阶段）

关闭 KVM 后，`arch/arm64/kvm/arch_timer.o` 不再参与链接，但 `drivers/irqchip/irq-mbigen.c` 中仍有：

```c
extern bool vtimer_irqbypass;
```

并在 `vtimer_mbigen_device_probe()` 使用，导致链接期错误：

```text
drivers/irqchip/irq-mbigen.o: undefined reference to `vtimer_irqbypass'
```

同时，由于 `CONFIG_HISILICON_IRQ_MBIGEN` 被其他 Kconfig `select`，简单 `-d` 无法关闭，`make olddefconfig` 会自动重新打开。

最终采用 **局部 stub 方式**：在 `irq-mbigen.c` 中根据 `CONFIG_KVM` 的开关提供一个安全的默认实现。

修改步骤：

1. 打开文件：

   ```bash
   vim drivers/irqchip/irq-mbigen.c
   ```

2. 找到原来的声明：

   ```c
   extern bool vtimer_irqbypass;
   ```

3. 替换为以下代码：

   ```c
   #if IS_ENABLED(CONFIG_KVM)
   extern bool vtimer_irqbypass;
   #else
   /*
    * KVM 关闭时，这个驱动仍然会被编译。
    * 这里提供一个仅在本文件可见的 dummy 变量，避免链接时缺失符号。
    * 关闭 irqbypass 功能（默认 false）是安全的退化行为。
    */
   static bool vtimer_irqbypass;
   #endif
   ```

4. 增量编译验证：

   ```bash
   make drivers/irqchip/irq-mbigen.o
   ```

   若通过，再继续完整构建。

---

## 7. 最终构建步骤（合并配置 + 修补后）

完成上述所有配置调整和 `irq-mbigen.c` 修改之后，在源码根目录执行：

```bash
cd ~/tmp-2/openEuler-5.10.0-216-src
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-

make -j"$(nproc)" Image dtbs modules

mkdir -p ~/tmp-2/rootfs-merged
make modules_install INSTALL_MOD_PATH=~/tmp-2/rootfs-merged
```

期望输出：

* 内核镜像：

  ```bash
  ls -lh arch/arm64/boot/Image
  ```

* 开发板设备树：

  ```bash
  ls arch/arm64/boot/dts/phytium/pd2008-devboard-dsk.dtb
  ```

* 模块目录：

  ```bash
  ls ~/tmp-2/rootfs-merged/lib/modules
  ```

* vmlinux / System.map（可选检查）：

  ```bash
  ls -lh vmlinux System.map
  ```

如果能正常看到这些文件，并且构建过程最后出现类似：

```text
LD      vmlinux
BTF     .btf.vmlinux.bin.o
LD      vmlinux.o
LD      vmlinux
SORTTAB vmlinux
SYSMAP  System.map
```

则说明整套「openEuler Server .config + Phytium BSP + pd2008 DTS」的内核已经编译成功，可用于后续上板测试。

---

## 8. 实习生复现注意事项

1. **不要跳步骤**
   按文档顺序执行，尤其是配置调整（`scripts/config -d ...`）和 `irq-mbigen.c` 的修改。

2. **每次修改配置后都跑 `make olddefconfig`**
   保证依赖关系合法，避免奇怪的 Kconfig 冲突。

3. **只要遇到新的编译 / 链接错误，先记录原始错误再改**
   不要随便乱删代码；先确认是不是不必要的驱动，再选择关掉或 stub。

4. 目前禁用的功能：

    * Phytium DRM 显示控制器（`CONFIG_DRM_PHYTIUM`）
    * SDMA DAE（`CONFIG_SDMA_DAE`）
    * KVM 及虚拟化相关（至少 `CONFIG_KVM` 关闭）
    * MBIGEN 中对 KVM 变量的依赖由 stub 处理

   对 D2000 作为服务器使用、开发 PCIe / NVMe / 网络驱动没有影响。

后续如果需要补上 KVM、IOMMU SVA、显示等功能，再单独从飞腾 Yocto 原内核里挑选补丁，逐项打开即可。


