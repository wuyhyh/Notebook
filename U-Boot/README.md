# U-Boot

以下是 U-Boot 项目 README 文件的第一部分中文翻译，对应原文中的 **Summary（概述）**、**Status（状态）**、**Where to get
help（获取帮助）**、**Where to get source code（获取源代码）**、**Where we come from（项目起源）** 和 **Names and Spelling（命名规范）**：

---

## 项目概述（Summary）

这个目录包含了 **U-Boot** 的源代码。U-Boot 是一款面向嵌入式开发板的引导加载程序（boot loader），支持 PowerPC、ARM、MIPS
等多种处理器架构。它可以被安装在启动 ROM 中，用于初始化与测试硬件，或者用于下载并运行应用程序代码。

U-Boot 的开发与 Linux 密切相关：其中部分源代码源自 Linux 源码树，两者共享部分头文件，同时 U-Boot 特别提供了引导 Linux
镜像的支持。

U-Boot 在设计时特别强调了配置与扩展的灵活性。例如，所有监控命令都使用相同的调用接口，非常容易添加新命令。而对于不常用的功能（如硬件测试工具），可以动态加载运行，而不是永久内置在监控程序中。

---

## 当前状态（Status）

通常情况下，所有在 `configs/` 目录下存在默认配置文件的开发板都已经在某种程度上被测试过，并可以认为是“可工作的”。事实上，其中许多板子已在实际生产系统中使用。

如果遇到问题，可以使用以下命令查找相关负责人：

```bash
scripts/get_maintainer.pl <path>
```

或者查看 Git 提交历史了解相关信息。

---

## 获取帮助（Where to get help）

如果你对 U-Boot 有任何问题、困惑或贡献，应该发邮件到 U-Boot 邮件列表：

* 邮件地址: `u-boot@lists.denx.de`
* 邮件归档：

    * [https://lists.denx.de/pipermail/u-boot](https://lists.denx.de/pipermail/u-boot)
    * [https://marc.info/?l=u-boot](https://marc.info/?l=u-boot)

建议在提问之前先搜索邮件归档以避免重复提问常见问题（FAQ）。

---

## 获取源代码（Where to get source code）

U-Boot 的源代码托管在 Git 仓库中：

* Git 仓库地址：
  [https://source.denx.de/u-boot/u-boot.git](https://source.denx.de/u-boot/u-boot.git)
* 在线浏览代码页面：
  [https://source.denx.de/u-boot/u-boot](https://source.denx.de/u-boot/u-boot)

页面的 “Tags” 链接允许你下载任意版本的 tarball 包。官方版本也可以通过 DENX 文件服务器获取：

* HTTPS: [https://ftp.denx.de/pub/u-boot/](https://ftp.denx.de/pub/u-boot/)
* FTP: ftp\://ftp.denx.de/pub/u-boot/

---

## 项目起源（Where we come from）

* 最初起源于 `8xxrom` 项目
* 创建了 `PPCBoot` 项目（[https://sourceforge.net/projects/ppcboot）](https://sourceforge.net/projects/ppcboot）)

    * 清理代码
    * 更易于添加自定义开发板
    * 支持添加其他 PowerPC CPU
    * 增加功能，特别是：

        * 提供扩展的 Linux 引导接口
        * 支持 S-Record 下载
        * 支持网络引导
        * 支持 ATA/SCSI 硬盘引导
* 创建了 `ARMBoot` 项目（[https://sourceforge.net/projects/armboot）](https://sourceforge.net/projects/armboot）)
* 增加对其他 CPU 架构（从 ARM 开始）的支持
* 最终创建 `U-Boot` 项目（[https://sourceforge.net/projects/u-boot）](https://sourceforge.net/projects/u-boot）)
* 当前项目页面：[https://www.denx.de/wiki/U-Boot](https://www.denx.de/wiki/U-Boot)

---

## 命名与拼写规范（Names and Spelling）

* 项目的正式名称是 **“Das U-Boot”**

* 所有文档和源代码中应使用 “U-Boot” 这一拼写，例如：

  ```
  这是 U-Boot 项目的 README 文件。
  ```

* 文件名应基于字符串 “u-boot”，如：

  ```c++
  include/asm-ppc/u-boot.h
  #include <asm/u-boot.h>
  ```

* 变量名、预处理常量应使用 “u\_boot” 或 “U\_BOOT” 为前缀，例如：

  ```c++
  U_BOOT_VERSION    u_boot_logo
  IH_OS_U_BOOT      u_boot_hush_start
  ```

---

你可以说“继续”查看下一部分（将进入 Software Configuration 和 sandbox 环境等内容）。是否继续？
