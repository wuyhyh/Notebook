这个页面是 U-Boot 官方文档中的一节，标题为 **Measured Boot（度量启动）**，链接为：

[https://docs.u-boot.org/en/latest/usage/measured\_boot.html](https://docs.u-boot.org/en/latest/usage/measured_boot.html)

它的主要内容是介绍 **U-Boot 如何支持 Measured Boot（度量启动）机制**，并结合 TPM（Trusted Platform
Module，可信平台模块）对启动过程中各个阶段的组件进行度量，以支持可信计算。

---

## ✅ 主要内容概述：

### 一、什么是 Measured Boot？

Measured Boot（度量启动）是一种安全机制，其核心思想是：

> **将启动过程中加载的关键组件进行哈希计算（度量），并把这些度量值记录到 TPM（可信平台模块）的 PCR（Platform Configuration
Registers）中。**

* 目的是提供一个可信链（Chain of Trust）；
* 后续系统（比如操作系统、安全验证工具）可以根据 TPM 中的度量值验证启动流程是否被篡改。

---

### 二、U-Boot 如何支持 Measured Boot？

U-Boot 的 Measured Boot 实现依赖以下组件：

#### 1. TPM 模块（Trusted Platform Module）

* U-Boot 要编译并启用对 TPM 的支持；
* 使用 TPM 2.0 驱动，和 `tpm2_*` 命令集交互。

#### 2. IMA（Integrity Measurement Architecture）

* U-Boot 支持将度量数据按照 IMA 格式封装；
* 生成的 IMA 事件日志可以由 Linux 内核读取并继续接力度量链。

---

### 三、启动过程中的度量目标（可配置）：

U-Boot 可以度量以下对象：

* U-Boot 自身的二进制
* FIT 镜像中的内核（kernel）、设备树（fdt）、initramfs 等
* 外部加载的 bootloader 或启动脚本

这些组件会被计算 hash 值（通常是 SHA-256），并记录到 TPM 中。

---

### 四、配置方法（简要）：

启用 measured boot 功能，需要在配置文件中加入：

```c
#define CONFIG_MEASURED_BOOT
#define CONFIG_TPM2
#define CONFIG_IMA_EVM
```

并根据实际平台启用 TPM 驱动，例如：

```c
#define CONFIG_TPM2_MMIO
#define CONFIG_TPM2_BASE_ADDRESS 0xabcdef00
```

---

### 五、事件日志（Event Log）

* 所有度量操作都会生成一份 IMA 风格的 event log；
* 日志保存在内存中，在 Linux 内核启动后可以访问；
* 可以用于验证启动流程的完整性。

---

### 六、典型使用流程：

1. U-Boot 启动并初始化 TPM；
2. 度量自身和加载的镜像（如 kernel、fdt）；
3. 把哈希值写入 TPM 的 PCR；
4. 生成 event log；
5. 启动 Linux；
6. Linux 可以读取 TPM PCR 和 event log，验证启动路径是否完整、未被篡改。

---

## ✅ 总结表：

| 项目   | 内容                               |
|------|----------------------------------|
| 功能   | 度量 U-Boot 启动过程中加载的关键组件，提升系统可信性   |
| 依赖   | TPM2.0、IMA（完整性度量架构）              |
| 支持对象 | U-Boot 本身、kernel、fdt、initramfs 等 |
| 输出   | 写入 TPM PCR 值 + 生成 event log      |
| 使用场景 | 安全启动链、可信计算、Linux IMA/EVM 安全子系统   |
| 限制   | 需要平台有 TPM 芯片或模拟器支持               |

---

Measured Boot 是在 Secure Boot 基础上进一步增强可信性的机制。如果你未来涉及可信引导、安全系统、或者嵌入式设备的安全性开发，这一机制非常关键。

是否需要我为你画一个“启动链信任度量流程图”来帮助理解整个过程？
