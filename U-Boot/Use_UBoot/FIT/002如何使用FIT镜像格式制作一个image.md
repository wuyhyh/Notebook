这个网页是 U-Boot 文档中 FIT 功能的关键章节之一，标题为 **“How to use FIT images”**，重点介绍了如何创建、配置和加载 *
*FIT（Flattened Image Tree）格式的镜像文件**，是使用 FIT 功能的入门和实践指南。

---

## 🧭 主要内容概览：

### 📌 什么是 FIT Image？

FIT（Flattened Image Tree）是 U-Boot 引入的一种镜像打包格式，用来替代传统的
uImage，它可以将多个组件（如内核、设备树、initramfs）组合在一个镜像文件中，并支持签名、安全校验等功能。

---

## 🛠️ 一步步教你使用 FIT Image

### 1. **创建 `.its` 文件（Image Tree Source）**

`.its` 文件是用来描述 FIT 镜像结构的文本文件，其格式类似于 DTS。

示例结构包括：

* 一个或多个 **kernel** 节点；
* 一个或多个 **fdt**（设备树）节点；
* 可选的 **ramdisk** 或 **loadables**；
* 配置（`config@1`）节指定了默认启动的组合。

```dts
/dts-v1/;

/ {
	description = "Simple FIT image";

	images {
		kernel@1 {
			description = "Linux Kernel";
			data = /
			incbin/("zImage");
			type = "kernel";
			arch = "arm";
			os = "linux";
			compression = "none";
			load = <0x80008000>;
			entry = <0x80008000>;

			hash@1 {
				algo = "sha1";
			};
		};

		fdt@1 {
			description = "Flattened Device Tree blob";
			data = /
			incbin/("my-board.dtb");
			type = "flat_dt";
			arch = "arm";
			compression = "none";

			hash@1 {
				algo = "sha1";
			};
		};
	};

	configurations {
		default = "conf@1";

		conf@1 {
			kernel = "kernel@1";
			fdt = "fdt@1";
		};
	};
};
```

---

### 2. **使用 mkimage 工具生成 .itb 文件**

```sh
mkimage -f fitImage.its fitImage.itb
```

* `-f` 表示输入的 `.its` 文件；
* `fitImage.itb` 是输出的二进制 FIT 镜像。

你也可以加入签名（后面会提到）。

---

### 3. **在 U-Boot 中加载 FIT 镜像**

在 U-Boot 命令行中加载 `.itb` 镜像的常用命令：

```sh
load mmc 0:1 0x81000000 fitImage.itb
bootm 0x81000000
```

* `bootm` 可以直接解析 `.itb` 文件结构，识别里面的 kernel、fdt、ramdisk；
* U-Boot 会自动从配置节中选择 default 的启动配置。

---

### 4. **签名与安全（可选）**

* 支持对 kernel、dtb、ramdisk 等每个部分进行哈希、签名；
* 支持 **RSA、SHA1、SHA256** 等算法；
* 可以生成 key-pair 用于验证；
* 公钥可以嵌入到 U-Boot 的设备树中进行签名校验。

---

### 5. **高级功能：多配置与动态加载**

* 支持多个配置（多个 kernel + dtb 组合）；
* 可以在运行时指定 boot 配置：

  ```sh
  setenv fdtfile my-board-v2.dtb
  bootm $loadaddr#conf@v2
  ```

---

## 📌 FIT 与传统 uImage 区别

| 项目     | uImage                                  | FIT Image                |
|--------|-----------------------------------------|--------------------------|
| 多组件支持  | 否（只能包含内核）                               | 是（可包含 kernel、dtb、initrd） |
| 签名校验   | 否                                       | 是                        |
| 安全启动支持 | 否                                       | 是                        |
| 配置灵活性  | 差                                       | 强，支持多个配置                 |
| 使用方式   | `mkimage -A arm -O linux -T kernel ...` | `mkimage -f xxx.its`     |

---

## 🧠 小贴士：

* `.its` 文件其实是你定义“系统启动需要什么”的地方；
* U-Boot 通过 `bootm` 解析 `.itb` 的结构；
* 一般 `.itb` 文件放在 SD 卡、SPI NOR 或 eMMC 中；
* 用 `dumpimage -l fitImage.itb` 可以查看镜像结构；
* 你可以在 `.its` 文件中内联多个 dtb、多个内核，构成一个多版本适配镜像。

---

## ✅ 总结一句话：

> 这个文档教你如何通过 `.its` + `mkimage` 制作一个功能强大、结构灵活、支持签名校验的 **FIT 镜像**，以便在 U-Boot
> 启动时统一加载内核、设备树和其他组件，是构建可信、安全嵌入式系统的关键工具之一。

---

如果你希望我为你手动写一个适配你平台的 `.its` 文件模板，或者帮你分析你已有的 `.itb` 结构，也可以继续发我内容。是否继续看下一个页面？
