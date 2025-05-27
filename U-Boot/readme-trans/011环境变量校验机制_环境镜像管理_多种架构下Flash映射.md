继续翻译 U-Boot README，以下是 **第 11 部分** 的翻译，内容包括：

* 环境变量校验机制（类型验证）
* 环境镜像的存放与加载
* 错误容错机制（如 CRC 校验）
* 特殊架构下的地址映射（如 sandbox 模式）
* X86 复位向量设置

---

### ✅ 环境变量类型验证与访问控制

通过定义以下宏，可以控制环境变量的合法值与访问权限：

#### 🧩 校验宏定义：

* `CONFIG_ENV_FLAGS_LIST_DEFAULT`
  定义 `.flags` 环境变量中默认的验证规则

* `CFG_ENV_FLAGS_LIST_STATIC`
  如果 `.flags` 中未包含某个变量，将使用该静态规则列表

#### 🧩 校验格式说明：

每个条目格式如下：

```
变量名[:属性]
```

其中，属性由两部分组成：

* **类型属性（type attribute）**：

    * `s`：字符串（默认）
    * `d`：十进制数
    * `x`：十六进制数
    * `b`：布尔值（1yYtT/0nNfF）
    * `i`：IP 地址
    * `m`：MAC 地址

* **访问属性（access attribute）**：

    * `a`：可读写（默认）
    * `r`：只读
    * `o`：只写一次
    * `c`：只能改默认值

示例：

```bash
ethaddr:ma,bootdelay:da
```

> 如果启用了 `CONFIG_REGEX`，变量名部分会作为正则表达式处理，从而允许一条规则匹配多个变量。

---

### ✅ 环境镜像的存放与加载

首次访问环境变量发生在 U-Boot 初始化早期（如读取串口波特率），因此必须保证环境存储区域已映射可访问。

即使设备支持 NVRAM 存储，U-Boot 仍会在 RAM 中维护一个副本，确保只有在调用 `saveenv` 命令时才写回 NVRAM，防止误修改。

---

### ✅ 特殊设备的只读环境

某些设备从远程 NOR Flash（通过 SRIO、PCIe 等）读取环境变量，但无法写入。在这种情况下，**`saveenv` 命令不可用**。

---

### ✅ NAND 环境加载位置配置

* `CONFIG_NAND_ENV_DST`
  SPL 启动时会将环境变量镜像从 NAND 拷贝至此 RAM 地址。

  若启用了冗余环境机制，会使用：

  ```
  CONFIG_NAND_ENV_DST + CONFIG_ENV_SIZE
  ```

---

### ✅ 环境 CRC 校验机制

环境变量通过 CRC32 校验以检测损坏：

* 在 U-Boot 重定位（relocate）之前，若 CRC 校验失败，会自动加载编译时内置的默认环境（**静默回退**）；
* 重定位完成后若 CRC 错误，系统将提示报错；
* 一旦执行了 `saveenv` 保存操作，会重新生成有效的 CRC。

---

### ✅ 网络状态检测（PHY 链路）

* `CONFIG_SYS_FAULT_MII_ADDR`
  指定用于检测以太网链路状态的 PHY 地址。

---

### ✅ 启动信息显示配置

* `CONFIG_DISPLAY_BOARDINFO`
  启动时调用 `checkboard()`，打印开发板信息。

* `CONFIG_DISPLAY_BOARDINFO_LATE`
  在标准 IO 系统（如 LCD）初始化后再打印板级信息。

---

### ✅ 虚拟地址映射支持（Sandbox 环境）

* `CONFIG_ARCH_MAP_SYSMEM`
  默认情况下，U-Boot 使用“有效地址”直接访问内存。但对于 sandbox 环境，其 RAM 是模拟的，必须通过 `map_sysmem()` /
  `unmap_sysmem()` 映射地址。

---

### ✅ x86 复位向量配置

* `CONFIG_X86_RESET_VECTOR`
  启用 x86 复位向量代码（当 U-Boot 不通过 Coreboot 启动时启用）

---

下一部分将翻译 Freescale QE / FMAN / Layerscape 固件支持、构建流程说明等内容，是否继续？

