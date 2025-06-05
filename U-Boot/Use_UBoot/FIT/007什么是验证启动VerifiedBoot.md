这个页面标题是：

> **Verified Boot using FIT**

这是 U-Boot 中 **FIT 签名功能最核心的安全用例文档**，主要描述如何利用 FIT（Flattened Image Tree）格式实现完整的 **Verified
Boot（验证启动）机制**，确保启动的内核和设备树没有被篡改。

---

## ✅ 一句话总结：

> 本文讲解如何使用 FIT 镜像 + 签名机制，结合 RSA 签名和公钥验证，在 U-Boot 中实现**安全启动链（Verified Boot）**
> ，防止加载恶意或被篡改的镜像文件。

---

## 📚 文档主要内容概览：

---

### 1. 🔐 什么是 Verified Boot？

**Verified Boot（验证启动）** 是一种机制：

* 每个启动组件（kernel、dtb、initrd）都有哈希和签名；
* 使用可信的 **公钥** 验证签名；
* 如果签名验证失败，则阻止系统继续启动。

这可确保：

* 系统启动的是**可信的官方镜像**；
* 防止**篡改、恶意替换、注入后门**。

---

### 2. 🧱 FIT 镜像在 Verified Boot 中的作用

* FIT 支持多组件封装（kernel、fdt、initrd、firmware）；
* 可对每个组件 **单独做哈希 + 签名**；
* 支持多个配置（多系统、多板卡）；
* 支持嵌入签名结构，公钥保存在 U-Boot 的设备树中。

---

### 3. 🔧 启用 Verified Boot 的编译配置（Kconfig）

要启用该功能，你需要在 U-Boot 编译时设置如下宏：

```c
CONFIG_FIT
CONFIG_FIT_SIGNATURE
CONFIG_RSA
CONFIG_OF_CONTROL
CONFIG_DM
CONFIG_SPL_FIT_SIGNATURE     // 如果要 SPL 阶段也验证
```

---

### 4. 🗂️ `.its` 文件结构中签名的定义

签名是通过 `signatures` 节定义的：

```dts
signatures {
	signature@1 {
		algo = "sha256,rsa2048";
		key-name-hint = "dev";
		sign-images = "kernel", "fdt", "ramdisk";
	};
}
```

配合每个镜像条目中定义 `hash@1`，例如：

```dts
kernel@1 {
	...

	hash@1 {
		algo = "sha256";
	};
}
```

---

### 5. 🔑 密钥的生成与管理

* 用 `openssl` 生成 RSA 密钥对；
* 私钥用于生成签名；
* 公钥需要编译进 U-Boot 的设备树（DTS）中；
* 使用 `mkimage -k` 工具将公钥自动注入设备树；

```sh
openssl genpkey -algorithm RSA -out dev.key -pkeyopt rsa_keygen_bits:2048
openssl rsa -in dev.key -pubout -out dev.pub

mkimage -k keys/ -r -f fit.its fit.itb
```

---

### 6. 🧪 启动验证流程

启动时使用命令：

```sh
bootm ${loadaddr}
```

U-Boot 会：

1. 解包 `.itb`；
2. 找到 `signatures`；
3. 校验 hash；
4. 用 DTS 中的公钥验证签名；
5. 失败则报错，停止启动。

---

### 7. ✅ 安全链的完整流程图：

**签名制作端：**

```
  kernel, dtb, initrd
       ↓
  计算 hash
       ↓
  用私钥签名
       ↓
  打包为 .itb 镜像
```

**启动验证端（U-Boot）：**

```
加载 .itb
    ↓
提取签名字段和公钥
    ↓
验证各组件 hash 和签名
    ↓
通过则 bootm 启动
失败则中断启动
```

---

## 📌 总结重点：

| 项目     | 内容                            |
|--------|-------------------------------|
| 验证目的   | 确保启动的 kernel、fdt、initrd 未被篡改  |
| 签名方式   | 使用 RSA 私钥生成签名，公钥编译进 U-Boot    |
| 校验机制   | U-Boot `bootm` 命令内置签名检查流程     |
| 安全等级   | 可与 Secure Boot/TPM 等一起构建完整信任链 |
| 典型应用场景 | 嵌入式设备、IoT、安全网关、可信计算平台         |

---

## 🧠 附加建议：

* 建议用 2048 位或以上的 RSA 密钥；
* 如果你用 SPL 启动，也需要在 SPL 中启用签名验证（`CONFIG_SPL_FIT_SIGNATURE`）；
* 如果公钥位于外部 flash，你可以在运行时读取并注册到 U-Boot 的 keyring 中。

---

如果你正在设计一个自己的设备验证启动方案，我可以帮你写完整的 `.its` + 签名脚本，并指导你如何将公钥嵌入设备树或动态加载。

是否继续分析下一个页面？
