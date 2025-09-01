# LFS 第7章：虚拟内核文件系统（/dev、/proc、/sys、/run、devpts）

> 目标：系统性梳理“虚拟内核文件系统”的概念、历史演化、职责划分、/dev 与 /sys 的区别、kobject/sysfs 的动机与实现机制，以及在
> LFS 第 7 章中如何正确挂载/卸载这些文件系统。

---

## 1. 什么是“虚拟内核文件系统”？

**虚拟内核文件系统（Virtual Kernel File Systems）** 并非存放于磁盘的真实文件，而是内核在内存中动态生成的“文件接口”。它们将*
*内核状态、硬件信息和控制入口**以“像文件一样可读写”的方式暴露给用户空间，使我们能用熟悉的 `cat`、`echo`、`ls` 等工具与内核交互。

常见成员：

* **/dev**：设备文件（字符/块设备节点、特殊设备），是**与驱动进行数据交互**的入口。
* **/proc**（procfs）：系统与进程的**运行时信息**视图（如 `/proc/cpuinfo`、`/proc/[pid]/`）。
* **/sys**（sysfs）：内核对象模型（kobject）的**信息与配置接口**，呈现硬件/驱动/总线/类的层次结构。
* **/run**（tmpfs）：运行期的**易失性数据**（PID、锁、socket 等）。
* **devpts**：为\*\*伪终端（PTY）\*\*提供的虚拟文件系统（挂载到 `/dev/pts`）。

---

## 2. 为什么会有这么多种？（历史与分工）

这是**历史演进 + 职责分离**的结果：

* **早期 /dev**：Unix 传统用“设备文件”表示硬件（如 `/dev/sda`），适合作为**数据通道**，但不适合承载大量**属性/层次信息**。
* **1990s 的 /proc**：初衷是**进程信息**，后来扩展到大量系统/硬件状态，逐渐显得**臃肿且混杂**。
* **Linux 2.6 引入 /sys**：将硬件与驱动相关的属性从 `/proc` 中剥离，构建**内核对象模型（kobject）+ sysfs**，提供层次化、统一且可扩展的
  **信息/配置**接口。
* **/run**：替代早期 `/var/run` 的磁盘路径，使用内存型 tmpfs，**在系统早期即可可用**，放置 PID、socket 等运行期数据。
* **devpts**：为动态数量的伪终端提供专用支持。

> 总结：不是重复造轮子，而是**各司其职**：`/dev` 侧重“数据 I/O”，`/proc` 侧重“运行态观察”，`/sys` 侧重“对象模型 + 属性/配置”，
`/run` 侧重“早期可用的临时运行数据”，`devpts` 侧重“PTY”。

---

## 3. /dev 与 /sys：本质区别一图懂

| 维度   | /dev                                     | /sys                                            |
|------|------------------------------------------|-------------------------------------------------|
| 本质   | 设备节点（字符/块/特殊设备文件）                        | kobject 的属性视图（目录+属性文件）                          |
| 主要用途 | **数据通道**：读写设备、ioctl                      | **信息/配置**：查询属性、调整参数                             |
| 典型操作 | `read/write/ioctl` 驱动的 `file_operations` | `cat/echo` 触发 `show/store` 回调                   |
| 信息组织 | 扁平目录（历史遗留）                               | 层次化拓扑（总线→设备→驱动→类）                               |
| 谁来生成 | 早期 `mknod`；现代 **udev** 动态创建设备节点          | 内核/驱动注册 kobject 时由 **sysfs** 自动呈现               |
| 示例   | `/dev/sda`、`/dev/ttyS0`、`/dev/null`      | `/sys/class/net/eth0/mtu`、`/sys/block/sda/size` |

**类比**：

* `/dev` 像“**设备插口**”：插上就能收发数据。
* `/sys` 像“**说明书+旋钮**”：可读属性，可调参数，可见拓扑关系。

---

## 4. 引入 kobject/sysfs 的动机（为什么不是把一切都塞进 /dev？）

* `/dev` 更擅长**数据流**，不擅长表达**属性与层次**；靠 `ioctl` 扩展既不直观也难统一。
* 需要一个统一、可扩展、层次化的**对象模型**：

    * **设备 (device)**、**驱动 (driver)**、**总线 (bus)**、**类 (class)** 都抽象成 **kobject**；
    * 每个对象有自己的**属性文件**；
    * 通过 sysfs 呈现完整的**设备拓扑**（`/sys/devices/...`）、**按类聚合**（`/sys/class/...`）。
* 为用户空间自动化提供基石：

    * **uevent**（内核事件） + **udev**：即插即用、自动命名/创建设备节点。

> 结果：`/dev` 专注“访问入口”，`/sys` 专注“对象与属性”。两者分工清晰、工具链统一、可扩展性更好。

---

## 5. `/sys` 的数据从哪里来？kobject 谁初始化？

* **来源**：驱动/子系统将对象注册到内核设备模型时，内置的 `kobject` 被初始化与注册；对应目录/属性由 **sysfs** 暴露在
  `/sys`。
* **主体**：

    * 设备（`struct device`，内部含 `struct kobject kobj`） → `device_register()`；
    * 驱动（`struct device_driver`） → `driver_register()`；
    * 总线（`struct bus_type`） → 内核在启动或模块加载时注册；
    * 类（`struct class`） → 子系统注册（如 `class_create()`）。
* **属性文件**：以 `kobj_attribute` 形式挂接，用户 `cat`/`echo` 时调用驱动提供的 `show/store` 回调。

**示例（简化）**：

```c++
static ssize_t my_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf)
{
    return sysfs_emit(buf, "%d\n", 42); // 读属性
}

static ssize_t my_store(struct kobject *kobj, struct kobj_attribute *attr,
                        const char *buf, size_t count)
{
    // 解析并应用新值...
    return count; // 写属性
}

static struct kobj_attribute my_attr = __ATTR(my_value, 0644, my_show, my_store);

// 注册阶段：
// sysfs_create_file(kobj, &my_attr.attr); // kobj 通常来源于 device/driver/bus/class
```

---

## 6. `/dev` 的内容从哪里来？（mknod vs udev）

* **传统做法**：系统管理员 `mknod /dev/sda b 8 0` 静态创建（`b`=块，`c`=字符）。
* **现代做法**：

    1. 设备/驱动注册 → 内核为其分配 **major/minor** 并触发 **uevent**；
    2. **udevd** 监听事件，读取 `/sys` 下的属性（类型、别名、权限、序列号等）；
    3. udev 根据规则在 `/dev` 下动态**创建设备节点**（并可建立友好命名的符号链接）。

> 因此，`/dev` 的呈现依赖 `/sys` 的元信息，`/sys` 则源于内核设备模型。两者相辅相成。

---

## 7. 关系总览（ASCII 示意）

```
驱动/子系统注册
      │
      ▼
  +-----------+         触发 uevent         +-----------------+
  |  kobject  | ─────────────────────────▶  |   udevd (用户态) |
  +-----------+                             +-----------------+
      │ 通过 sysfs
      ▼
 /sys/...  ←—— 属性(读/写)、拓扑、类视图
      │                                   │
      └───────────────(读取属性/规则)───────┘
                                           │ 创建设备节点
                                           ▼
                                        /dev/...

应用程序：
- 通过 /dev 与驱动进行 **数据交互**（read/write/ioctl）
- 通过 /sys **查询/调优** 驱动与设备属性（cat/echo → show/store）
```

---

## 8. LFS 第 7 章：在 chroot 前正确挂载

进入 chroot 前，必须把宿主机的虚拟内核文件系统挂载到新系统根下，否则 chroot 内部将无法访问设备与系统信息。

```bash
# 绑定宿主机 /dev（设备节点）
mount -v --bind /dev $LFS/dev

# 伪终端（PTY）支持
a) mkdir -p $LFS/dev/pts
b) mount -vt devpts devpts $LFS/dev/pts -o gid=5,mode=620

# 进程/系统状态
a) mount -vt proc  proc  $LFS/proc

# 设备/驱动/总线/类（sysfs）
a) mount -vt sysfs sysfs $LFS/sys

# 运行期（tmpfs）
a) mount -vt tmpfs tmpfs $LFS/run
```

**验证挂载：**

```bash
mount | egrep "on ($LFS/dev|$LFS/dev/pts|$LFS/proc|$LFS/sys|$LFS/run)"
```

**进入 chroot：**

```bash
chroot "$LFS" /usr/bin/env -i \
    HOME=/root TERM="$TERM" PS1='(lfs chroot) # ' \
    PATH=/usr/bin:/usr/sbin \
    /bin/bash --login
```

**退出 chroot / 卸载顺序建议（反向卸载）**：

```bash
exit  # 离开 chroot
umount -v $LFS/dev/pts
umount -v $LFS/dev
umount -v $LFS/proc
umount -v $LFS/sys
umount -v $LFS/run
```

> 注意：若提示 busy，可用 `fuser -vm` 或 `lsof` 排查哪个进程占用，或使用 `umount -l`（懒卸载，谨慎）。

---

## 9. 常用观察与练习清单（建议亲手操作）

* **观察 CPU/内存/进程**：

  ```bash
  cat /proc/cpuinfo
  cat /proc/meminfo
  ls -l /proc/$$   # 当前 shell 进程目录
  ```
* **观察设备拓扑**：

  ```bash
  tree -L 3 /sys/devices | less
  ls -l /sys/class/net
  cat /sys/block/sda/size
  ```
* **调节设备属性（示例：网卡 MTU）**：

  ```bash
  cat /sys/class/net/eth0/mtu
  echo 1400 | sudo tee /sys/class/net/eth0/mtu
  ```
* **查看 udev 动态节点与属性**：

  ```bash
  udevadm info -a -p $(udevadm info -q path -n /dev/sda)
  ```

---

## 10. 记忆法总结

* 用途分类：

    * **/dev** = 硬件“插口”（数据通道）。
    * **/proc** = 系统“体检报告”（运行时状态）。
    * **/sys** = “说明书+旋钮”（对象模型与配置）。
    * **/run** = 运行期“便签”（易失性数据）。
    * **/dev/pts** = 伪终端的“座位号”。
* 历史脉络：`/proc` 过度泛化 → `/sys` 承担设备模型；`/var/run` 启动早期不可用 → `/run`（tmpfs）。
* 联系图谱：**驱动注册 → kobject/sysfs → uevent → udev → /dev 节点**；应用通过 `/dev` 做 I/O，通过 `/sys` 查/调参数。

---

## 11. FAQ 速查

* **为什么不能只用 /dev？**  因为 `/dev` 是 I/O 通道，难以统一表达属性/层次，`ioctl` 不直观且不统一。
* **/sys 会不会多余？**  它为设备管理提供了统一的对象模型与属性接口，是现代自动化（udev/systemd）的基础。
* **kobject 我需要手写吗？**  通常**不需要直接手写**：使用驱动/子系统提供的注册 API（`device_register`、`class_create`
  等）即可，kobject 随对象初始化。
* **/dev 的节点是谁建的？**  现代系统由 **udev** 根据内核 **uevent** 和 `/sys` 信息动态创建。

---

## 12. 参考实现线索（进一步阅读）

* 内核源码路径（不同版本略有差异）：

    * 设备模型：`drivers/base/`、`include/linux/device.h`
    * kobject/sysfs：`lib/kobject.c`、`fs/sysfs/`
    * procfs：`fs/proc/`
    * devpts：`fs/devpts/`
