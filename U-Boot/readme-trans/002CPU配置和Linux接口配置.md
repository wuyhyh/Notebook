继续翻译 U-Boot README，以下是 **sandbox 环境相关配置选项** 的翻译（包括部分通用 CPU 配置和 Linux 接口配置）：

---

## 配置选项详解（节选自 sandbox 部分之后）

### ✅ CPU 类型设置

必须定义一个具体的 CPU 类型，例如：

```c
CONFIG_MPC85XX
```

---

### ✅ 开发板类型设置

也必须定义一个具体的开发板类型，例如：

```c
CONFIG_MPC8540ADS
```

---

### ✅ MPC85xx CPU 特定配置（示例）

* `CONFIG_SYS_PPC64`
  指定核心为 64 位 PowerPC 架构，符合 Power ISA “64” 分类（例如 ePAPR 规范要求）。

* `CONFIG_SYS_FSL_ERRATUM_A004510`
  启用对 Erratum A004510 的修复；如果启用，需同时设置以下两个选项：

    * `CONFIG_SYS_FSL_ERRATUM_A004510_SVR_REV`

    * `CFG_SYS_FSL_CORENET_SNOOPVEC_COREONLY`

  > Freescale App Note 4493 中有详细说明。

* `CFG_SYS_FSL_CORENET_SNOOPVEC_COREONLY`
  表示根据 A004510 补丁，应在 CCSR 寄存器偏移 0x18600 处写入的值。

---

### ✅ 通用 CPU 配置选项

* `CONFIG_SYS_FSL_DDR`
  启用 Freescale DDR 控制器驱动。适用于 mpc83xx、mpc85xx 及部分 ARM SoC。

* `CFG_SYS_FSL_DDR_ADDR`
  DDR 控制器的内存映射寄存器基地址。

* `CONFIG_SYS_FSL_IFC_CLK_DIV`
  配置平台时钟到 IFC 控制器的分频比。

* `CONFIG_SYS_FSL_LBC_CLK_DIV`
  配置平台时钟到 eLBC 控制器的分频比。

* `CFG_SYS_FSL_DDR_SDRAM_BASE_PHY`
  从 DDR 控制器视角的物理地址。对于 Power SoC 来说，这个地址通常等于 `CFG_SYS_DDR_SDRAM_BASE`，但对于 ARM SoC 可能不同。

---

### ✅ ARM 特定配置

* `CFG_SYS_EXCEPTION_VECTORS_HIGH`
  选择 ARM 核心使用高地址的异常向量表（即不清除 CP15 的 c1 寄存器的 V 位）。

* `COUNTER_FREQUENCY`
  通用定时器的时钟频率。

* `COUNTER_FREQUENCY_REAL`
  如果实际时钟频率运行时才能确定，与 `COUNTER_FREQUENCY` 不同时设置此项。

---

### ✅ Linux 内核接口配置

* `CONFIG_OF_LIBFDT`
  支持基于 FDT（扁平设备树）的内核引导方式。

    * 启用 `fdt` 命令
    * `bootm` 命令会自动更新设备树（fdt）

* `OF_TBCLK`
  时间基准频率（timebase clock frequency）

* `OF_QE`
  支持使用 QUICC Engine 的板子设置 UCC MAC 地址。

* `CONFIG_OF_IDE_FIXUP`
  如果未连接 IDE 设备，U-Boot 可以自动从设备树中移除对应节点，避免 Linux 探测失败崩溃（例如 uc101 板子上 IDE5V\_DD7
  信号无下拉电阻）。

---

下一个部分将包含 vxWorks 引导、Cache 设置、串口支持、命令裁剪选项、IO trace、时间戳等配置说明。

是否继续？还是只翻你关心的部分（比如串口、USB、SPI、DDR、NAND、MTD 等）？


