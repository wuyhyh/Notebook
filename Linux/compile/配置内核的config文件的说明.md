你问的这几个问题都非常关键，是很多第一次手动编译 Linux 内核的开发者会遇到的疑惑。下面我一一解答：

---

## ✅ 问题 1：`cp /boot/config-$(uname -r) .config` 与 `make defconfig`、`make olddefconfig` 有什么区别？

| 命令                                    | 作用                                                    |
|---------------------------------------|-------------------------------------------------------|
| `make defconfig`                      | 根据架构默认的内核配置生成 `.config`，是 **内核维护者推荐的最小配置**。适合纯净环境开始构建 |
| `cp /boot/config-$(uname -r) .config` | 使用当前系统正在运行的 Fedora（或其他发行版）内核的配置，适合 **保持系统现有特性**       |
| `make olddefconfig`                   | 在已有 `.config` 基础上，**保持原配置**，同时为新内核中新增的配置使用默认值补全       |

### 推荐搭配（用于保留原系统配置）：

```bash
cp /boot/config-$(uname -r) .config
make olddefconfig
```

这一步非常重要，能让你编译的 vanilla 内核具备原系统的功能（如网络、显卡驱动、BPF 等），否则新内核启动可能功能不完整。

---

## ✅ 问题 2：`make menuconfig` 的过程是怎样的？

`make menuconfig` 是基于 ncurses 的文本界面配置工具，用来编辑 `.config` 文件。

### 步骤如下：

```bash
make menuconfig
```

然后你会看到一个基于终端的交互菜单：

```
 ┌────────────────────────────────── Linux Kernel Configuration ──────────────────────────────────┐
 │  Arrow keys navigate the menu.  <Enter> selects submenus --->.                                 │
 │  Highlighted letters are hotkeys.  Pressing <Y> includes, <N> excludes, <M> modularizes        │
 │                                                                                                │
 │  [*] General setup  --->                                                                       │
 │  [ ] Enable loadable module support  --->                                                      │
 │  [ ] Processor type and features  --->                                                         │
 │  [ ] Networking support  --->                                                                  │
 │                                                                                                │
 │<Select>    <Exit>    <Help>                                                                    │
 └────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 常用按键：

| 键                  | 功能                      |
|--------------------|-------------------------|
| `上下箭头`             | 选择菜单项                   |
| `Enter`            | 进入子菜单                   |
| `Y/N/M`            | 选择是否启用选项（Yes/No/Module） |
| `/`                | 搜索配置项（支持关键词或宏名）         |
| `Esc Esc`          | 返回上层菜单                  |
| `Tab` 切换到 `<Save>` | 保存配置                    |
| 保存后生成 `.config` 文件 |                         |

这一步主要用于**开启/关闭某些功能或驱动支持**，比如：

* 开启 BPF/BTF 支持
* 开启某个特定文件系统
* 去除 debug 功能缩小内核体积

---

## ✅ 问题 3：是否可以提前指定重启时从新内核启动？（不等到手动进 grub）

是的，有多种方式可以在**重启前提前设置默认启动内核**或**仅下一次重启使用某个内核**。

### 🧭 方法一：设置默认启动项（永久生效）

```bash
# 查看可用启动项索引
sudo grub2-editenv list
awk -F\' '$1=="menuentry " {print i++ " : " $2}' /etc/grub2.cfg
```

然后设置默认：

```bash
sudo grub2-set-default 2   # 比如设为第3个（索引从0开始）
```

> 重启后会默认进入第 2 号启动项。

---

### 🔁 方法二：只在下一次启动中使用指定内核（推荐测试新内核）

```bash
sudo grub2-reboot 2
sudo reboot
```

* 上述命令只在**下一次重启时**启动第 2 个内核启动项；
* 下下次仍回到默认启动项。

---

### 💡 额外说明

* Fedora 在使用 UEFI 时，可能需要用：

```bash
# BIOS 启动系统
/etc/grub2.cfg

# UEFI 启动系统（大部分现代机器）
/etc/grub2-efi.cfg 或 /boot/efi/EFI/fedora/grub.cfg
```

确保你查看的 grub 配置文件是正确的。

---

## ✅ 总结表

| 需求         | 推荐命令                                                       |
|------------|------------------------------------------------------------|
| 快速获取系统原有配置 | `cp /boot/config-$(uname -r) .config && make olddefconfig` |
| 默认配置构建     | `make defconfig`                                           |
| 图形化选择模块    | `make menuconfig`                                          |
| 设置永久启动新内核  | `sudo grub2-set-default N`                                 |
| 只下次启动用新内核  | `sudo grub2-reboot N`                                      |

---

如果你愿意，我可以帮你梳理一份完整的从 vanilla 源码编译 → 安装 → 配置 → 启动切换 → 卸载旧内核 的全流程脚本。是否需要？

# 完整的 vanilla 内核编译、安装、启动流程（UEFI 专用）

---

## ✅ 问题 1：在执行 `make menuconfig` 之前需要准备 `.config` 文件吗？

取决于你是否希望**复用当前系统的配置**：

### ✅ 推荐操作：

```bash
cp /boot/config-$(uname -r) .config
make olddefconfig     # 补齐新内核中新增的配置项
make menuconfig       # 此时进去就是完整的、系统当前的配置基础
```

### 📌 为什么不直接 `make menuconfig`？

如果你不手动准备 `.config` 文件，那么：

* 会使用默认的 `defconfig`（通常是针对某些架构的最小功能集）
* 很多你当前系统需要的驱动和模块不会启用
* 编译出的内核可能无法驱动你的网络、显卡等

### 总结：

| 操作                                              | 是否建议  | 原因          |
|-------------------------------------------------|-------|-------------|
| 直接 `make menuconfig`                            | ❌ 不建议 | 缺少当前系统配置基础  |
| 先 `cp config && make olddefconfig` 再 menuconfig | ✅ 推荐  | 保留现有功能并可自定义 |

---

## ✅ 问题 2：UEFI 系统中 grub 配置和默认项设置命令

Fedora UEFI 系统的 grub 配置文件在：

```
/boot/efi/EFI/fedora/grub.cfg
```

但这是由 `/etc/grub2-efi.cfg` 链接生成的，一般我们使用如下命令管理 grub：

### 🧭 1. 生成 grub 配置文件

```bash
sudo grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg
```

或者（两者等价）：

```bash
sudo grub2-mkconfig -o /etc/grub2-efi.cfg
```

### 🔁 2. 设置下次重启临时使用某个内核（索引从 0 开始）

```bash
sudo grub2-reboot 1
sudo reboot
```

### 🖥️ 3. 设置默认启动项

```bash
sudo grub2-set-default 1
```

### 👀 4. 查看当前启动项索引和列表

```bash
awk -F\' '$1=="menuentry " {print i++ " : " $2}' /boot/efi/EFI/fedora/grub.cfg
```

---







可以的！在 `make menuconfig` 中确实可以**修改编译出来的内核的“名字”**，也就是 `uname -r` 输出的内核标识 —— 它是通过 `EXTRAVERSION` 或 `CONFIG_LOCALVERSION` 来控制的。

---

## ✅ 方法一：使用 `CONFIG_LOCALVERSION` 设置后缀（推荐）

在 `make menuconfig` 中：

```text
General setup  --->
    () Local version - append to kernel release
```

就是 `CONFIG_LOCALVERSION`。

你可以设置为：

```
(-custom) Local version - append to kernel release
```

比如你填了：

```text
-custom
```

然后编译出来的内核版本就变成：

```bash
6.16.0+-custom
```

这个字符串会体现在：

* `/boot/vmlinuz-6.16.0+-custom`
* `/boot/loader/entries/...6.16.0+-custom.conf`
* `uname -r` 输出为 `6.16.0+-custom`

---

## ✅ 方法二：编辑 Makefile 中的 `EXTRAVERSION`

打开顶层 `Makefile`，找到：

```make
VERSION = 6
PATCHLEVEL = 16
SUBLEVEL = 0
EXTRAVERSION =
```

你可以将其修改为：

```make
EXTRAVERSION = -custom
```

同样会影响 `uname -r` 输出，例如：

```bash
6.16.0-custom
```

> ⚠️ 如果同时设置了 `EXTRAVERSION` 和 `CONFIG_LOCALVERSION`，它们会拼接！

例如：

```make
EXTRAVERSION = -custom
```

配合

```
CONFIG_LOCALVERSION = -debug
```

结果是：

```bash
6.16.0-custom-debug
```

---

## 📌 建议使用哪种方式？

| 方法                    | 修改位置                     | 优点          | 推荐使用场景      |
| --------------------- | ------------------------ | ----------- | ----------- |
| `CONFIG_LOCALVERSION` | `menuconfig` 或 `.config` | 最灵活、无侵入     | 自定义一次性内核    |
| `EXTRAVERSION`        | 顶层 `Makefile`            | 编译同系列内核的基础名 | 系统化维护多个内核版本 |

---

## ✅ 总结速查

| 操作                           | 作用                   |
| ---------------------------- | -------------------- |
| `CONFIG_LOCALVERSION="-foo"` | 通过 menuconfig 设置后缀名  |
| `EXTRAVERSION = -bar`        | 修改 Makefile 添加内核版本后缀 |
| `uname -r`                   | 查看最终内核名（含后缀）         |
| `/boot/vmlinuz-*`            | 文件名也会带上这个后缀          |

---

需要我帮你写一个自动设置 `CONFIG_LOCALVERSION` 并构建的脚本，也可以继续告诉我。

