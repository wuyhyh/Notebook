继续翻译 U-Boot README，以下是 **第 7 部分** 的翻译，涵盖：

* I2C 总线与多路复用配置
* 软件 I2C 支持（Soft I2C）
* SPI 支持
* FPGA 支持

---

### ✅ I2C 支持（I2C Support）

* `CFG_SYS_NUM_I2C_BUSES`：指定要使用的 I2C 总线数量
* `CFG_SYS_I2C_BUSES`：定义所有 I2C 总线的配置（总线号、I2C 多路复用器类型、地址、端口）

> 示例配置：

```c
CFG_SYS_I2C_BUSES {
  {0, {I2C_NULL_HOP}},                          // 总线 0，无 MUX
  {0, {{I2C_MUX_PCA9547, 0x70, 1}}},            // 总线 1，MUX 地址 0x70，端口 1
  {1, {I2C_NULL_HOP}},                          // 总线 6，无 MUX
}
```

> 如果板子上没有 I2C 多路复用器，可不定义 `CFG_SYS_I2C_BUSES`。

---

### ✅ 软件 I2C 接口支持（Legacy I2C Support）

当使用 **软件模拟 I2C（CONFIG\_SYS\_I2C\_SOFT）** 时，需要定义以下宏以控制引脚：

* `I2C_INIT`：初始化 GPIO 设置（如方向为输出）
* `I2C_ACTIVE`：设置 SDA 为驱动模式
* `I2C_TRISTATE`：设置 SDA 为高阻态
* `I2C_READ`：读取 SDA 电平（高/低）
* `I2C_SDA(bit)`：将 SDA 设置为 1（高）或 0（低）
* `I2C_SCL(bit)`：将 SCL 设置为 1 或 0
* `I2C_DELAY`：每个时钟周期延时，控制传输速率
  示例：

  ```c
  #define I2C_DELAY udelay(2)
  ```

#### GPIO 式软件 I2C（适用于使用 Linux 通用 GPIO 框架的架构）

* `CONFIG_SOFT_I2C_GPIO_SCL` / `CONFIG_SOFT_I2C_GPIO_SDA`：直接定义使用哪个 GPIO 编号作为 SCL/SDA

---

### ✅ 跳过特定 I2C 设备的探测

* `CFG_SYS_I2C_NOPROBES`：定义一组地址，在运行 `i2c probe` 命令时将跳过这些地址
  示例：

  ```c
  #define CFG_SYS_I2C_NOPROBES {0x50, 0x68}
  ```

---

### ✅ 强制重复起始位读取（Repeated Start）

* `CONFIG_SOFT_I2C_READ_REPEATED_START`：启用后，`i2c_read()` 将在写地址指针后立即发起重复起始位，而不是 stop → start 组合

  > 某些设备要求使用重复起始方式读取数据。

---

### ✅ SPI 支持（SPI Support）

* `CONFIG_SPI`：启用 SPI 驱动

* `CFG_SYS_SPI_MXC_WAIT`：等待 SPI 传输完成的超时时间（默认 10 毫秒）
  示例：

  ```c
  #define CFG_SYS_SPI_MXC_WAIT (CONFIG_SYS_HZ / 100)
  ```

---

### ✅ FPGA 支持（FPGA Support）

* `CONFIG_FPGA`：启用 FPGA 子系统

* `CONFIG_FPGA_<vendor>`：支持具体 FPGA 厂商（如 `ALTERA`、`XILINX`）

* `CONFIG_FPGA_<family>`：支持具体 FPGA 系列（如 `SPARTAN2`, `VIRTEX2`）

#### 可选配置宏：

* `CONFIG_SYS_FPGA_CHECK_BUSY`：配置时检查 FPGA 接口的繁忙状态
* `CFG_FPGA_DELAY`：FPGA 配置过程中使用的延迟函数
* `CFG_SYS_FPGA_CHECK_ERROR`：检测 FPGA 配置错误（如 CRC 错误）
* `CFG_SYS_FPGA_WAIT_INIT`：等待 INIT\_B 信号恢复的最大时间（默认 500 ms）
* `CFG_SYS_FPGA_WAIT_BUSY`：等待 BUSY 信号解除的最大时间（默认 5 ms）
* `CFG_SYS_FPGA_WAIT_CONFIG`：配置完成后的等待时间（默认 200 ms）

---

下一部分将包括：

* 厂商参数保护（如 ethaddr、serial#）
* 预留 RAM 区域（Protected RAM）
* 错误恢复行为
* 默认环境变量配置
* 自动 TFTP 更新

是否继续？

