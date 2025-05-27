继续翻译 U-Boot README，以下为下一部分内容，涵盖：

* **软件配置（Software Configuration）**
* **sandbox 执行环境（Sandbox Environment）**

---

## 软件配置（Software Configuration）

### 处理器架构与开发板类型的选择

对于所有受支持的开发板，U-Boot 都提供了现成的默认配置文件。你只需运行以下命令即可：

```bash
make <board_name>_defconfig
```

例如，对于 TQM823L 模块：

```bash
cd u-boot
make TQM823L_defconfig
```

> **注意：**
> 如果你发现某些开发板的配置文件缺失，请查看 `doc/README.scrapyard`，该文件列出了已不再支持的开发板。

---

## sandbox 执行环境（Sandbox Environment）

U-Boot 可以**在本机 Linux 系统上原生构建运行**，使用一种称为 `sandbox` 的虚拟开发板。这种机制有如下优势：

* 可以开发与硬件无关的功能
* 便于在桌面环境中进行测试和调试
* 也是运行部分 U-Boot 单元测试的主要平台

更多详细信息可查看文档：

```
doc/arch/sandbox/sandbox.rst
```

---

接下来的部分是关于 **各种配置宏** 的详解，比如 CPU 类型、DDR 控制器设置、串口参数、FDT
支持等。是否要继续翻译这部分内容？你也可以指定只翻某些模块（如串口、DDR、网络、USB 等）。是否继续？


