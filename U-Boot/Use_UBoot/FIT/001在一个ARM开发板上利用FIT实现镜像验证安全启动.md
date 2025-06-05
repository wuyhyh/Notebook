这个网页是 U-Boot 官方文档中的一节，标题为 **“Verified Boot with FIT on BeagleBone Black”**，主要讲的是如何在 BeagleBone
Black 上使用 **FIT (Flattened Image Tree)** 配合 **Verified Boot（验证启动）** 的机制来增强安全性。

下面是这篇文档中的关键信息总结和分析：

---

### 🌟 核心目的：

通过 **FIT image** 实现一种 **安全启动（Verified Boot）机制**，使用 **公钥加密签名** 来验证 Linux 内核、设备树和 initramfs
的完整性，防止加载未经授权的镜像。

---

### ✅ 背景和前提：

* **BeagleBone Black** 是一个广泛使用的 ARM 开发板，它的 U-Boot 支持使用 FIT image。
* 为了实现验证启动，你需要：

    * 启用支持 FIT 配置的 U-Boot；
    * 为你的镜像签名；
    * 并在运行时由 U-Boot 验证签名。

---

### 🛠️ 实现步骤（逐条解析）：

#### 1. 准备 FIT description `.its` 文件：

* 这是一个描述 FIT image 结构的脚本格式（类似 DTS）。
* 指定了包含的内核镜像、设备树文件和 initramfs；
* 也指定了这些组件的 SHA 校验方式（如 sha1、sha256）；
* 如果启用签名，还要包含签名信息、密钥引用等。

```its
kernel@1 {
    description = "kernel";
    data = /incbin/("zImage");
    type = "kernel";
    arch = "arm";
    os = "linux";
    compression = "none";
    load = <0x80007fc0>;
    entry = <0x80007fc0>;
    hash@1 {
        algo = "sha1";
    };
};
```

#### 2. 生成密钥对：

* 使用 OpenSSL 生成 RSA 密钥对。

  ```sh
  openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048
  openssl rsa -in private_key.pem -pubout -out public_key.pem
  ```

#### 3. 使用 `mkimage` 构建 FIT image：

* `mkimage` 是 U-Boot 提供的工具，可用于将 `.its` 文件打包成 `.itb`（FIT binary）文件。

  ```sh
  mkimage -f fitImage.its fitImage.itb
  ```

#### 4. 将公钥编译进 U-Boot：

* 使用 `mkimage -k` 生成设备树格式的公钥文件；
* 然后将其 include 到 board 的 U-Boot DTS 中，以便 U-Boot 能验证签名。

```sh
mkimage -D "-I dts -O dtb -p 2048" -k keys -r -f fitImage.its fitImage.itb
```

---

### 🔒 签名验证机制：

* FIT image 结构里可以嵌入签名（通常是 RSA 签名）；
* U-Boot 加载时会用公钥验证镜像签名；
* 如果签名验证失败，镜像就不会被加载，从而达到防篡改的目的。

---

### 📌 注意事项：

* 要使用验证启动功能，U-Boot 需配置以下宏：

  ```c
  CONFIG_FIT
  CONFIG_FIT_SIGNATURE
  CONFIG_RSA
  CONFIG_OF_CONTROL
  CONFIG_DM
  ```
* 开发时可以启用 `CONFIG_SPL_FIT_SIGNATURE` 以便在 SPL 阶段也进行验证；
* 确保 U-Boot 本身的 DTS 中包含了公钥节点。

---

### 📚 总结一句话：

这个文档展示了如何在 BeagleBone Black 上用 U-Boot 的 **FIT 镜像格式** 配合 **RSA 签名机制** 实现一个**完整性验证的安全启动过程
**，是一种在嵌入式设备中构建可信链条的典型方法。

---

如果你想让我也翻译 `.its` 文件结构或讲解如何改写它，或者帮你实践在你的设备上制作 `.itb`，我可以继续辅助。你还想继续分析下一个网页吗？
