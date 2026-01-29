# SMP problem

试试指定单核启动，启动了20次都没有出现问题。

```shell
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=1 nosmp nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

你现在已经把问题收敛到一个非常硬的结论：**只要把 SMP 真正关掉（`nosmp`/`nr_cpus=1` 生效），系统就稳定**
。接下来要做的是“二分法”把触发条件进一步变成一个最小可复现组合，然后再判断是 **CPU online/SMP bring-up** 触发，还是 **SMP
运行时（中断/负载均衡/PCIe MSI/电源管理）** 触发。


---

# 实验 1

## 第 0 步：先确认到底是哪一个开关在起作用

你现在同时用了 `nr_cpus=1` 和 `nosmp`。先拆开它们，确定谁是关键。

### 0-A：只留 `nr_cpus=1`，去掉 `nosmp`

```sh
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=1 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

### 0-B：只留 `nosmp`，去掉 `nr_cpus=1`

```sh
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nosmp nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

> 结论：A B 均稳定

结果解读：

* 如果 **0-A 稳定、0-B 也稳定**：两者都有效，后面用 `nr_cpus` 做“递增核数”更方便。
* 如果 **只有 0-A 稳定**：说明你这平台上 `nosmp` 可能被某些路径绕过/表现异常，但 `nr_cpus` 能真限核数（很常见）。
* 如果 **只有 0-B 稳定**：说明 `nr_cpus` 没真正限住（也可能是你这套内核解析时序/平台怪异）。

---

## 第 1 步：构造“最小复现”的 SMP 配置（从 2 核开始）

目标是找到“从稳到崩”的第一刀，通常就是 2 核。

如果你第 0 步确认 `nr_cpus` 有效，那就直接做：

### 1-A：`nr_cpus=2`（不加 nosmp）

```sh
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=2 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

如果 2 核就崩，说明问题跟 “SMP 一旦存在就触发” 强相关；如果 2 核不崩，再上 3/4 核，直到出现崩溃的最小核数 N。

> CON: 2 cores pass

```sh
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=3 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

> CON: 3 cores pass

```sh
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=4 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

> CON: 4 cores pass

```sh
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=5 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

> CON: 5 cores pass

```sh
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=6 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

> CON: 6 cores pass

```sh
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=7 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

> CON: 7 cores fail


> 你之前日志里出现过 “CPU6/CPU7 被 online”，而你认为已经单核，这种“核号/online 行为异常”本身就提示：**CPU online/拓扑/中断亲和性
** 这条链路很可疑。用 `nr_cpus=2` 能最快把复现压到最小。

> 最小崩溃核心数 N = 7

---

# 实验 2

我先把你这份“nr_cpus=7 才崩”的启动日志里真正的 panic 栈和触发点找出来，再根据 CPU 拓扑/PSCI/GIC/调度器路径给你一个最短的定位矩阵（下一步只需要做
3-4 次启动实验）。

我先把你这次“nr_cpus=7 会崩溃、1-6 稳”的现象和你给的启动日志关键点对齐一下，然后给出最可能的根因链路，以及下一步最省时间的验证/定位步骤（含可以直接改
bootargs 的试验矩阵）。

你现在把范围缩得很漂亮了：**1–6 核稳定，只有 `nr_cpus=7` 会崩**。下一步别再靠“反复改 `nr_cpus`”撞运气了，用更可控的方法把“到底是第
7 个核本身的问题，还是 `nr_cpus` 触发了内核数组裁剪后的越界/内存破坏”区分开。

## 1) 先把这次 `nr_cpus=7` 的崩溃点钉死

你的 `nr_cpus=7` 启动日志里，内核明确提示 **8 核被裁成 7 核**：
`Number of cores (8) exceeds configured maximum of 7 - clipping`
随后在 **CPU2（swapper/2）** 上发生 **IABT**，`pc : 0xe0`、`lr : ktime_get+0x4c/0xac`，最终 panic 。
`pc=0xe0` 这种非常像“跳到野指针/函数指针被破坏”的结果，而不太像正常代码路径里的确定性 NULL 解引用。

另外你启动早期还有一个很关键的 **GICv3 IRQ translate 警告**，调用栈里带 `phytium_ixic_alloc -> of_irq_parse_and_map_pci`
。这类告警本身不一定立刻致命，但它很像“IRQ/MSI/中断域参数不对”，会导致后续出现非常诡异的内存/并发问题。

## 2) 核心思路：不要用 `nr_cpus` 做定位，改用 `maxcpus + 热插拔 online`

**原因**：`nr_cpus` 会把内核里大量 per-cpu 结构、位图、数组的上限直接裁小（你这里裁到 7） 。如果平台代码/驱动里有任何“还按 8
核去索引”的 bug，`nr_cpus=7` 会把它从“潜在 bug”变成“立刻内存破坏”。
而 `maxcpus` 只限制“启动时 bring-up 的 CPU 数”，**不会裁剪这些全局上限**，更适合做隔离实验。

### 实验 A（最关键，建议先做）：启动时只起 6 核，然后手动 online 第 7/8 核

U-Boot 启动参数建议这样改（保留你现在稳定的其余项）：

```bash
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
maxcpus=6 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd systemd.unit=multi-user.target'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

```bash
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
maxcpus=1 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd systemd.unit=multi-user.target'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

进系统后（串口上操作）：

```bash
cat /sys/devices/system/cpu/present
cat /sys/devices/system/cpu/online

# 先 online cpu6
echo 1 > /sys/devices/system/cpu/cpu6/online
dmesg | tail -n 80

# 再 online cpu7
echo 1 > /sys/devices/system/cpu/cpu7/online
dmesg | tail -n 80
```

**判读：**

* 如果 **online cpu6 就崩**：第 7 个核（大概率 MPID 0x300 那个簇/核）相关（PSCI/GICR/arch_timer/中断亲和性/平台 erratum）。
* 如果 cpu6 ok、但 **online cpu7 才崩**：第 8 个核相关。
* 如果两个都 ok，但一段时间后才崩：更像“多核并发/中断亲和性/某个驱动 race”。

这一步能把“是不是某个特定 CPU bring-up 就炸”直接定性。

> 实验 A 的结果是，使用 maxcpus 变量替换 nr_cpus 之后系统崩溃。

我先把你这两份“maxcpus=1/6 直接失败”的日志里真正的失败点（是卡死、panic、还是早期 bring-up）找出来，然后给出下一步最短的定位实验组合。

我已经定位到：maxcpus 路径和 nr_cpus 路径触发的崩溃都是“secondary_start_kernel / idle / 中断”附近的 Oops。下一步我把完整
call trace/PC/LR 函数名抓出来，才能判断是 cpuidle、GIC、还是 PSCI/CPU hotplug 相关。

我现在能确定“触发崩溃的就是逻辑 CPU6（第 7 个 online CPU）”，而且崩在 idle/中断路径上。接下来我把 maxcpus=1/6 为什么没把
CPU6 屏蔽掉这点也钉死，然后给你一个最小实验矩阵把问题压到 cpuidle/IRQ/固件三选一。

你现在已经把范围缩得很小了：**“第 7 个 online CPU（逻辑 CPU6）一上线就容易触发崩溃”**。你给的日志里，`maxcpus=6` 失败时就是 *
*CPU6 / swapper/6** 在 `secondary_start_kernel` 附近、走到 `cpuidle/arch_cpu_idle`，并且在中断路径里炸掉。
而 `maxcpus=1` 失败时，也能看到 **CPU6 / swapper/6** 报 soft lockup，说明 CPU6 其实还是被拉起来跑了。

关键点在这里：**你的 U-Boot/ATF 的 DT fixup 对 “maxcpus=” 的处理明显不靠谱**。不管你传 `maxcpus=1` 还是 `maxcpus=6`
，它都只打印“remove cpu@2/3/6/7”，完全不是按你给的值去裁 CPU，结果 CPU6 仍可能上线，照样触发崩溃。
反过来，你实验里 **`nr_cpus=1..6` 稳、`nr_cpus=7` 崩**，很符合“nr_cpus 真把逻辑 CPU6 挡在门外了”。

下面给你一个“最短实验矩阵”，继续把问题压到 **cpuidle / IRQ 路由 / 固件(PSCI/GIC)/硬件核** 里三选一。

---

> 结论：实验A采用
> setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \ earlycon=pl011,0x28001000 loglevel=8
> ignore_loglevel \ root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \ maxcpus=6 nmi_watchdog=0 panic=-1
> init=/lib/systemd/systemd systemd.unit=multi-user.target'
> 直接就失败了，我把maxcpu改成1也失败。与之前相比，
> nr_cpus变量还能撑到6，第7个核才崩溃。

# 实验 3

## 1) 先把“maxcpus 不生效”坐实（5 分钟搞定）

用会失败的那组 `maxcpus=1` 启动到能进系统的情况下（哪怕只坚持几十秒），立刻执行：

```sh
cat /proc/cmdline
cat /sys/devices/system/cpu/online
dmesg | grep -E "Booted secondary processor|CPU[0-9]+:" | head -n 80
```

如果 `online` 里出现了 `0-6` 或者 `0-7`，那就确认了：**maxcpus 在你这条启动链路里没把 CPU6 挡住**（结合你日志里 CPU6
还在跑，基本已经是事实）。

结论：后续定位时 **优先用 `nr_cpus=` 或者改 DT 禁核**，别再用 `maxcpus=` 做控制变量。

> CON:
> maxcpus参数无法进入用户态就失败了，读不到日志。

---

## 2) 用 4 条启动参数，把问题缩到“cpuidle vs 中断路由”

以你现在会崩的 `nr_cpus=7` 为基线（因为它会把 CPU6 拉起来），做下面 4 组对比，每组跑 20~30 分钟：

### 2.1 关闭 cpuidle（看是不是 WFI/PSCI suspend 导致 CPU6 死）

```bash
setenv bootargs '... rootwait nr_cpus=7 cpuidle.off=1 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
booti ...
```

```sh
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=7 cpuidle.off=1 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

再狠一点（比 cpuidle.off 更强），用：

```bash
... idle=poll
```

```shell
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=7 idle=poll nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

> 现象，cpuidle.off 10% 概率成功启动 idle=poll 6次全部失败

判定：

* **如果 `cpuidle.off=1`/`idle=poll` 后，`nr_cpus=7` 变稳定**：优先怀疑 **CPU6 的 idle state / PSCI cpu_suspend / 固件电源管理
  **（或者该核相关的时钟/电源域）问题。你日志里 CPU6 崩溃路径就在 `arch_cpu_idle -> cpuidle_enter_state` 附近，非常吻合。

### 2.2 把绝大多数 IRQ 固定到 0-5（看是不是 GIC/IRQ affinity 在 CPU6 上炸）

```bash
setenv bootargs '... rootwait nr_cpus=7 irqaffinity=0-5 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
booti ...
```

```shell
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=7 irqaffinity=0-5 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

> 现象：irqaffinity=0-5 10% 概率启动成功

判定：

* **如果加了 irqaffinity=0-5 就稳定**：优先怀疑 **GICv3 redistributor / per-cpu timer / IPI 路由** 在 CPU6 上有坑（IRQ 一进
  CPU6 就不对劲）。

### 2.3 组合拳（同时关 cpuidle + 固定 IRQ）

```bash
... nr_cpus=7 cpuidle.off=1 irqaffinity=0-5 ...
```

```shell
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=7 cpuidle.off=1 irqaffinity=0-5 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

> 结论：组合这两个参数还是概率性启动成功。

判定：

* 只有组合才稳：说明是“IRQ + idle 交互”触发（更偏固件/中断控制器配置）。
* 都不稳：那就偏向 **CPU6 本核硬件/一致性/异常向量** 之类（更硬的问题）。

---

## 3) 直接“禁用 cpu@300/cpu@301”绕开问题核，验证是不是单核硬伤

你的 DT 里 CPU 节点顺序基本是：`cpu@0,cpu@1,cpu@100,cpu@101,cpu@200,cpu@201,cpu@300,cpu@301`。
通常逻辑 CPU0..7 就按这个顺序映射，所以 **逻辑 CPU6/7 很可能对应 cpu@300/cpu@301**。

建议你做一个“禁核 DTB”作为长期 workaround + 定位手段：

1. 在能跑 dtc 的机器上：

```sh
dtc -I dtb -O dts -o pd2008.dts pd2008-devboard-dsk.dtb
```

2. 把 `cpu@300` 和 `cpu@301` 加上：

```dts
status = "disabled";
```

3. 编回 dtb：

```sh
dtc -I dts -O dtb -o pd2008-devboard-dsk.no_cpu67.dtb pd2008.dts
```

4. 上板启动时加载这个新 dtb，**不加 nr_cpus/maxcpus**（让它自然 SMP，但缺 cpu6/7）：

```bash
setenv bootargs '... rootwait nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.no_cpu67.dtb
booti ...
```

```shell
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.no_cpu67.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

> 现象，重新编译设备树还是启动后直接崩溃

判定：

* 如果这样长期稳定，那你就几乎可以把锅扣在 **“特定核（CPU6/7）或其所属 cluster 的 bring-up/IRQ/idle”** 上了，而不是
  systemd、rootfs 或 NVMe。

---

## 4) 你现在最值得继续推进的结论

1. **“nr_cpus=6 稳、nr_cpus=7 崩” 已经足够说明 CPU6 是触发点。**
2. **maxcpus 在你的启动链路里不可信**：U-Boot/ATF 的 DT fixup 输出在 `maxcpus=1` 和 `maxcpus=6` 下完全一样（都 remove
   cpu@2/3/6/7），这就解释了“maxcpus 改 1 也照样崩”。
3. 下一步别再扩散变量：按我上面 2.x 的四组启动参数跑一轮，你就能把范围从“第 7 核崩”进一步压到 **cpuidle / IRQ 路由 / 固件
   ** 里的某一个。

你跑完 2.1/2.2 的结果（只要告诉我：哪几组稳定、哪几组崩），我就能继续往下把“要改内核配置/要改 DT/要查 ATF/要查 GIC
redistributor 配置”的方向给你收敛到 1 条主线。

# 实验 4

我先把你上传的几份崩溃日志里“最关键的差异点”抽出来，然后给你一套下一步最省时间的二分/对照实验清单。

你现在这几组现象，其实已经把“范围”压到很小了：这是一个**SMP 相关**的问题，而且在失败样本里多次出现 **PC 跳到 0xe0**，并且 *
*LR 落在 `ktime_get()`**（也就是内核在读时间/clocksource 的路径上崩掉）。例如 `nr_cpus=7` 失败日志里：`pc : 0xe0`、
`lr : ktime_get+0x4c/0xac`，CPU=2（swapper/2）直接死。
你“关 CPU6/7 的 dtb”那份日志同样是 `pc : 0xe0`、`lr : ktime_get...`。
而 `cpuidle.off` 失败样本里也出现了 “Call trace: 0xe0 / Code: bad PC value”。

下面是我建议你**最省时间**的缩小范围路线（按优先级从高到低，做完前两步基本就能定位到“哪个 CPU/哪段硬件路径”）：

---

## 1) 先别再用 maxcpus 做结论，用 nr_cpus / nosmp 才靠谱

你已经观察到：`nr_cpus` 1–6 稳，7 崩；但 `maxcpus=1/6` 反而“直接失败”。这很正常：从你的失败日志看，`maxcpus=6` 时崩在 **CPU6
的早期/idle/IRQ 路径**（甚至出现 paging request / gic irq / cpuidle 路径）。
说明 **maxcpus 并没有像你想的那样阻止某些 CPU 早期跑起来**（至少在你这套内核/平台上不适合作为“限制核数”的实验变量）。后面所有二分实验，统一只用：

* “限制启动核数”：`nr_cpus=N` 或 `nosmp`
* “稳定复现崩溃”：`nr_cpus=7`（你的触发点）

---

## 2) 你“关 CPU6/7 的 dtb”大概率没关到“真正的第 7 个核”

关键点：你平台的 CPU 节点 **不是 cpu@0..cpu@7 这种顺序编号**，而是类似 MPIDR 风格：
`cpu@0 cpu@1 cpu@100 cpu@101 cpu@200 cpu@201 cpu@300 cpu@301`。

所以你把 `cpu@6`、`cpu@7` 关掉，**可能根本不是你以为的“第 7/8 个核”**；真正对应 “CPU6/CPU7（逻辑序号）” 的，往往是
`cpu@300/cpu@301` 这类节点（取决于内核枚举顺序）。

### 最快验证方式：别重新编 dtb，直接在 U-Boot 里现场禁用

开机进 U-Boot 后，用下面这套做一次（目的是：**把你认为有问题的那两个 CPU 节点准确 disable**）：

```bash
fdt addr ${fdt_addr_r}
fdt print /cpus

# 先观察到底有哪些 cpu@XXX 节点，通常能看到 cpu@0 cpu@1 cpu@100 ... cpu@301

# 然后禁用你要禁的节点（这里以 cpu@300 / cpu@301 为例）
fdt set /cpus/cpu@300 status "disabled"
fdt set /cpus/cpu@301 status "disabled"

# 再 print 一次确认 status 变了
fdt print /cpus/cpu@300
fdt print /cpus/cpu@301
```

接着**不带 nr_cpus**直接启动 systemd（保持你那套 bootargs 其它参数不动），看是否还会复现你“7 核必崩”的现象。

```shell
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

> 现象，还是启动就直接崩盘了

* 如果这样就稳定：基本坐实 **“某个特定 CPU（大概率就是第 7 个被 bringup 的核）相关：该核的 timer/irq/电源域/一致性/redistributor
  等”**。
* 如果还是会崩：那就不是单一坏核，而是 **SMP + 时间/中断路径的并发/内存破坏**（也仍然很集中，见第 4 步）。

---

## 3) 用“在线 CPU 热插拔”把问题从“开机概率”变成“可控触发”

你现在最痛的是“概率性成功/失败”。你已经有一个稳定点：`nr_cpus=6`。

下一步不要再 reboot 20 次赌概率了，改成：

1. 先用 `nr_cpus=6` 启动到系统稳定
2. 进入系统后再逐个 online：

```bash
# 看当前 cpu 数
lscpu | grep -E 'CPU\(s\)|On-line CPU'

# 依次 online（假设 cpu6/cpu7 存在）
echo 1 > /sys/devices/system/cpu/cpu6/online
dmesg -T | tail -n 200

echo 1 > /sys/devices/system/cpu/cpu7/online
dmesg -T | tail -n 200
```

> 现象：6核成功启动，但是没有开 hotplug, 执行失败。

这样你能把“触发点”压到非常具体：**是 online cpu6 立刻死，还是 cpu7，还是都不死但跑一会儿死**。
（如果你内核没开 CPU hotplug，这一步会失败；那就回到第 2 步用 dtb/uboot disable 来二分。）

---

## 4) 既然崩在 `ktime_get()`，就把 clocksource 固定住，验证是不是“某个时钟源/计时路径被破坏”

你失败日志里 `lr : ktime_get...` 非常关键：
这通常意味着：`ktime_get()` 里调用的底层“读时钟”路径出了问题（比如 clocksource 回调被破坏、或 timer/irq 乱导致 timekeeping
数据结构被踩）。

在你能稳定启动的场景（比如 `nr_cpus=6`）里先看可用 clocksource：

```bash
cat /sys/devices/system/clocksource/clocksource0/available_clocksource
cat /sys/devices/system/clocksource/clocksource0/current_clocksource
```

> 现象：只有 arch_sys_counter 这个 clocksource，无法切换。

然后做两类对照：

### A) 运行时强制切换 clocksource（不改内核不改 dtb）

```bash
echo arch_sys_counter > /sys/devices/system/clocksource/clocksource0/current_clocksource
```

### B) 启动参数里强制 clocksource（更干净）

bootargs 加：`clocksource=arch_sys_counter`（或者你 available 里最“标准”的那个）

如果强制某个 clocksource 后，“7 核必崩”明显改变（变稳定/变成另一种崩溃），那你就已经把问题从“泛 SMP”缩到了“时间源/计时 +
SMP”。

```sh
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=7 clocksource=arch_sys_counter nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```


```sh
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nr_cpus=7 nohz=off highres=off irqaffinity=0-5 nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```
nr_cpus=7 nohz=off highres=off irqaffinity=0-5


> 现象：系统强制指定 clocksource, 启动之后还是直接失败。

---

# 实验 5

我先把你当前的状态总结成几条硬结论（hotplug 未开、clocksource 单一、7核必崩），然后给你一条能落地的下一步：用
DT/内核配置把“问题核/问题路径”继续二分，并把崩溃从随机变成可抓的第一现场。

你这张图和你补充的信息，把路彻底指清了：

1. **CPU hotplug 没开**
   `/sys/devices/system/cpu/` 里只有 cpu0..cpu5，没有 cpu6 目录，所以你没法 `echo 1 > cpu6/online`。这很正常，不是你操作问题。
   结论：后续“在线逐个开核”的实验走不通，只能靠 **启动时 bring-up** 或 **DT 禁核** 来二分。

2. **clocksource 不是变量**
   available/current 都只有 `arch_sys_counter`，你加 `clocksource=arch_sys_counter` 不会改变任何东西。
   结论：你看到的 `ktime_get()` 崩溃，只能说明“时间路径被破坏/跳转到野地址”，但不是因为 clocksource 切换导致。

3. **真正的核心结论**
   你现在的稳定边界仍然是：**6 核稳定，7 核启动阶段就会把某个路径触发到崩溃**。这已经非常像“某个 CPU/cluster 的 bring-up
   过程中，IRQ/timer/PSCI/GICR 配置在某个点踩雷”，而不是用户态/systemd。

---

## 你下一步应该怎么缩小范围（不靠 hotplug，不靠 clocksource）

### A. 用 U-Boot FDT 动态禁核，把“是哪一对核/哪一个 cluster”分出来

你前面已经能在 U-Boot 里 `fdt print /cpus`，也看到了节点是：

* cpu@0 cpu@1 cpu@100 cpu@101 cpu@200 cpu@201 cpu@300 cpu@301

这通常是 4 个“簇/对核”。你现在默认稳定是 6 核，说明你很可能禁掉了其中一对或某对没 bring-up。

关键是：你不要只禁 cpu@300/cpu@301 一对就下结论，要做 **最小二分**：

1. 启动前在 U-Boot：

```bash
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb
fdt addr ${fdt_addr_r}
fdt resize 0x4000
fdt print /cpus
```

2. 只禁用一对核，分别做 4 轮（每次只禁一对）：

* 禁 cpu@0 + cpu@1
* 禁 cpu@100 + cpu@101
* 禁 cpu@200 + cpu@201
* 禁 cpu@300 + cpu@301

命令模板：

```bash
fdt set /cpus/cpu@0 status "disabled"
fdt set /cpus/cpu@1 status "disabled"
```

```bash
fdt set /cpus/cpu@100 status "disabled"
fdt set /cpus/cpu@101 status "disabled"
```

```bash
fdt set /cpus/cpu@200 status "disabled"
fdt set /cpus/cpu@201 status "disabled"
```

```bash
fdt set /cpus/cpu@300 status "disabled"
fdt set /cpus/cpu@301 status "disabled"
```

```bash
fdt print /cpus
```

```shell
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'
booti ${kernel_addr_r} - ${fdt_addr_r}
```

然后用同一套 bootargs 启动（不加 nr_cpus，让它自然 SMP），看哪一轮能稳定跑满（比如 30 分钟）。

完整的命令执行流程：

```shell
# 1) 读 kernel
ext4load nvme 0:2 ${kernel_addr_r} /boot/Image-5.10.0-baseline_2026Q1-2

# 2) 读 dtb（只读一次）
ext4load nvme 0:2 ${fdt_addr_r} /boot/dtb/pd2008-devboard-dsk.dtb

# 3) 指向并扩容（否则你之前会 FDT_ERR_NOSPACE）
fdt addr ${fdt_addr_r}
fdt resize 0x4000

# 4) 修改（禁用 cpu@300/cpu@301）
fdt set /cpus/cpu@300 status "disabled"
fdt set /cpus/cpu@301 status "disabled"

# 5) 验证（可选，但建议你每次做一下）
fdt print /cpus/cpu@300
fdt print /cpus/cpu@301

# 6) 设置 bootargs
setenv bootargs 'console=ttyAMA1,115200 console=ttyAMA0,115200 \
earlycon=pl011,0x28001000 loglevel=8 ignore_loglevel \
root=/dev/nvme0n1p2 rootfstype=ext4 rw rootwait \
nmi_watchdog=0 panic=-1 init=/lib/systemd/systemd'

# 7) 直接启动（这里不要再 ext4load dtb 了）
booti ${kernel_addr_r} - ${fdt_addr_r}
```

判读：

* 如果“禁掉某一对”后立刻变稳定，那问题就在那一对核（或对应簇的 GICR/计时器/电源域）。
* 如果不管禁哪一对都还是会在多核条件下崩，那问题更像是“多核并发触发的内存破坏”，不只是一对核。

> 现象：不管禁掉哪一对都会崩溃。

这一步是你现在最值钱的实验，因为它不需要改内核、不需要 hotplug，而且能把范围从“7 核”降到“哪一对 CPU”。

---

### B. 把崩溃从“跳到 0xe0 的野指针”提前抓住：打开内核的内存破坏检测（这是根治路线）

你现在看到的症状是“PC=0xe0 / bad PC value / ktime_get 附近”，这非常像 **内存被踩坏后随机跳转**。这种靠 bootargs
很难根治，必须靠内核配置把“第一次越界”抓出来。

你需要在内核 `.config` 里打开这些（优先级从高到低）：

1. **SLUB/页级调试（强烈推荐）**

* `CONFIG_SLUB_DEBUG=y`
* `CONFIG_SLUB_DEBUG_ON=y`（或用启动参数启用）
* `CONFIG_PAGE_POISONING=y`
* `CONFIG_DEBUG_PAGEALLOC=y`（性能损失大，但抓 bug 很有效）

对应启动参数（先从轻到重）：

* `slub_debug=FZPU page_poison=1`
* 如果还抓不到，再加：`debug_pagealloc=on`

2. **KASAN（如果你能接受性能/内存开销）**

* `CONFIG_KASAN=y`
* arm64 下通常配 `CONFIG_KASAN_SW_TAGS` 或普通模式，按你工具链能力选。

3. **锁/RCU/调度调试**

* `CONFIG_PROVE_LOCKING`
* `CONFIG_DEBUG_SPINLOCK`
* `CONFIG_RCU_TRACE`

你不用一次全开。我的建议是：先用 `SLUB_DEBUG + page_poison`，一般就能把“随机炸”变成“某个驱动/某个对象越界写”并给出更早、更一致的
call trace。

---

### C. 你现在为什么没法“6 核起来后再开第 7 核”

因为你没开 hotplug，这个判断是对的。要支持 sysfs online/offline，你至少需要：

* `CONFIG_HOTPLUG_CPU=y`

如果你愿意把 hotplug 打开，它会让你后续定位快一个数量级。但即使不开，你依然可以用上面 A 的“禁核二分”推进。

---

## 你现在应该立刻做的事（最短清单）

1. 在 U-Boot 用 `fdt resize 0x4000` 后，做“禁用一对核”的 4 轮二分，记录哪一轮稳定。
2. 同时准备一版“调试内核”：开 `SLUB_DEBUG + PAGE_POISONING`，并在 bootargs 加 `slub_debug=FZPU page_poison=1`，用
   `nr_cpus=7` 去复现，争取把 bug 变成可定位的第一次越界。

你把第 1 步 4 轮的结果（每轮大概多少核、是否稳定、如果崩溃最后一段 dmesg）发我，我就能告诉你：下一步是查 PSCI/GICR/arch_timer
还是去抓某个驱动的内存破坏。

