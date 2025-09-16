# ARM 嵌入式系统软件移植计划

## 1. U-Boot 开发

### 1.1 打包脚本  (已达成)

摸清打包脚本 DDR 训练、PCIe 工作模式配置、 PHY 配置、IOMMU/缓存一致性问题的解决办法

### 1.2 板级配置文件  (已达成)

- 编译板级配置文件丢失，根据 `.config` 文件还原了板级配置
- uboot 功能需要进一步定制，需要修改版级配置文件，使用 `menuconfig`修改编译组件

### 1.3 uboot 功能开发

#### 已达成：

启动参数和自定义命令开发

#### 待完成：

- 修改 uboot 设备树，增加 MAC 控制器驱动
- 校验 uboot 版本
- 加快启动时间

### 1.4 uboot 更新技术

#### 已达成：

- 使用网络 tftp 更新
- 使用串口更新

#### 待完成

- 使用 flash 芯片烧录器更新

## 2. 使用 QEMU 模拟

### 2.1 使用原版 QEMU 进行模拟自制开发板

#### 待完成：

先在 QEMU 里保证内核配置、文件系统、用户空间、通用驱动与基础启动链是健康的，再去攻克真机的板级差异

使用 QEMU 提供的 virt 平台模拟真实硬件，先把引导链跑通

### 2.2 使用飞腾提供的 firely 开发板模拟器

飞腾 bsp:

https://gitee.com/phytium_embedded/phytium-openeuler-embedded-bsp


#### 已达成：

使用飞腾的 firely 开发版提供的 bsp，移植 openEuler embedded 操作系统，使用 oe-build yocto 工程编译出
kernel dtb rootfs bootloader

#### 待完成：

- 设备树需要向自制开发板修正
- 需要移植内核模块编译工具链
- 需要移植 rdma-core 组件

### 2.3 oe-build

https://pages.openeuler.openatom.cn/embedded/docs/build/html/openEuler-22.03-LTS-SP4/yocto/index.html

## 3. 向真板收敛

### 3.1 官方 QEMU 方案 (待完成)

用两套 DTS：virt 专用 DTS（驱动主要走 virtio 与 QEMU 的标准外设），以及“真板” DTS。保持内核版本、工具链一致，缩小变量。

能用 QEMU 自带的设备模型就用（pl011、virtio-blk/net、dwmac、dwc2/3 等）；板上有“私有 IP”的，短期用 virtio 替代，后期再补驱动

启动链验证：若真板通过 TF-A 把 BL33 交给 U-Boot，在 QEMU 里用 -device loader 把 U-Boot 装到与真板约定的物理地址，模拟“Boot
ROM/BL31 跳转 BL33”的场景，尽量对齐入口地址与寄存器状态。

## 4. 调试开发板 (待完成)

### 4.1 直接调试

uboot 的启动参数中直接指定从 oe-build 的产物启动

### 4.2 调试 DPU RDMA 功能

### 4.3 PCIe 交换

# 远景规划

1. 使用 QEMU 对任意复杂硬件的完全模拟
2. 独立维护的嵌入式 Linux 发型版


