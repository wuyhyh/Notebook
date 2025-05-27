继续翻译 U-Boot README，以下是 **第 8 部分** 的翻译，涵盖：

* 厂商参数保护
* 预留 RAM 区域（Protected RAM）
* 错误恢复行为
* 默认环境变量
* 自动 TFTP 更新

---

### ✅ 厂商参数保护（Vendor Parameter Protection）

U-Boot 默认会保护两个关键环境变量不被随意修改：

* `serial#`（板子序列号）
* `ethaddr`（以太网 MAC 地址）

这两个变量视为**出厂唯一参数**，用户在正常使用中无法修改或删除。

如需禁用保护机制，有以下两种方式：

* 定义 `CONFIG_ENV_OVERWRITE`：完全允许修改任意环境变量（包括厂商参数）
* 使用 `.flags` 环境变量或静态验证宏 `CFG_ENV_FLAGS_LIST_STATIC`：对变量类型、访问权限等进行精细控制

---

### ✅ 预留 RAM（Protected RAM）

通过配置，可以保留一部分 RAM，避免被 U-Boot 或 Linux 使用：

* 定义 `CFG_PRAM`：设置预留 RAM 的默认大小（单位：KB）
* 用户还可设置环境变量 `pram` 来覆盖默认值
* `mem` 环境变量将自动生成，表示剩余可用内存（可用于传递给 Linux）
  示例：

  ```bash
  setenv bootargs ... mem=${mem}
  saveenv
  ```

> ⚠️ 注意：
>
> 如果你的板子采用自动内存探测，请确保该探测为**非破坏性**操作，否则会破坏 pram 区域。

---

### ✅ 错误恢复机制说明（Error Recovery）

环境变量有两类：

1. **局部变量（Local variables）**：
   使用 `name=value` 形式定义，通过 `$name` 或 `${name}` 引用。

2. **全局环境变量（Global variables）**：
   使用 `setenv` / `printenv` 操作，引用时用 `run` 命令，不能加 `$`。

⚠️ 在变量中存储命令或特殊字符时，建议使用双引号包裹整个字符串，而不是用反斜杠转义。

---

### ✅ 默认环境变量配置（Default Environment）

* `CFG_EXTRA_ENV_SETTINGS`
  可用于在编译时定义默认环境变量（键值对），内嵌在镜像中。

  示例：

  ```c++
  #define CFG_EXTRA_ENV_SETTINGS \
    "myvar1=value1\0" \
    "myvar2=value2\0"
  ```

  > ⚠️ 警告：
  >
  > 这种方式依赖于环境变量的内部存储结构，不保证向后兼容。请谨慎使用。

* `CONFIG_DELAY_ENVIRONMENT`
  启用后，环境变量不会在启动时立即加载，而是需要后续代码主动加载。

---

### ✅ 自动 TFTP 更新支持（Automatic software updates via TFTP）

* `CONFIG_UPDATE_TFTP`：启用自动 TFTP 下载更新功能
* `CONFIG_UPDATE_TFTP_CNT_MAX`：最大重试次数
* `CONFIG_UPDATE_TFTP_MSEC_MAX`：TFTP 超时时间（毫秒）

> 更多信息参见文档：`doc/README.update`

---

下一部分将翻译：

* MTD 支持（UBI 配置、wear leveling 等）
* SPL 子系统支持（小型引导加载器）
* 中断机制说明（PPC 架构）
* 板级初始化流程

是否继续？
