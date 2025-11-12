# openEuler/Yocto 去掉 APM 模块导致构建与启动异常——复盘

## 1. 背景与目标

* 平台：oebuild（Yocto/openEuler 24.03-LTS），`MACHINE=phytium`，目标架构 AArch64
* 需求：**从镜像中移除 APM 相关组件**（APM 仅适用于 x86 上的旧式电源管理；ARM64 上没意义），同时保证：

    * 构建阶段 `do_rootfs` 依赖解析不报错
    * 运行阶段系统能从 NVMe 分区稳定启动（双分区：`p1` 基线、`p2` 新版本）

---

## 2. 现象

1. 初始镜像启动日志出现：

```
Starting advanced power management daemon: No APM support in kernel (failed.)
```

2. 去掉 APM 后，有一次启动 **kernel panic**，panic 前错误为：

```
/sbin/init: error while loading shared libraries: /usr/lib64/libtirpc.so.3: file too short
```

3. 构建 `openeuler-image`/`openeuler-image-live` 时多次失败，典型报错：

```
file /etc/default/rcS conflicts between sysvinit-... and busybox-...
file /etc/init.d/rcS conflicts between sysvinit-... and busybox-...
```

---

## 3. 根因分析

* **APM 本身**：由 `packagegroup-base-apm`（以及 `apm/apmd` 包）引入，基于 x86 APM，ARM64 内核不支持，运行时必然失败。
* **panic 的直接原因**：`/usr/lib64/libtirpc.so.3: file too short`，属于**根文件系统损坏/半写**或**缺包**，与是否移除 APM
  无直接关系。
* **构建冲突**：镜像使用 **SysVinit** 时，`sysvinit` 与 `busybox` **都**提供了 `/etc/init.d/rcS`、`/etc/default/rcS`
  ，rpm/dnf 事务测试检测到**相同路径的真实文件**冲突而失败。发行层还带有一个 `busybox_%.bbappend`，会重新把 busybox 的 rcS
  文件放回，叠加冲突。

---

## 4. 解决方案（构建侧）

### 4.1 移除 APM 的正确方式

1. **local.conf** 去掉发行特性并钉基本运行时：

```text
DISTRO_FEATURES:remove = " apm systemd "
IMAGE_INSTALL:append   = " sysvinit sysvinit-inittab busybox libtirpc "
```

2. 在 **BSP 层**为 `packagegroup-base` 写 `bbappend`，同时移除三者：

查看配方分层

```text
bitbake-layers show-layers
```

```
meta-phytium/recipes-core/packagegroups/packagegroup-base.bbappend
```

```text
RDEPENDS:${PN}:remove     = " packagegroup-base-apm apm apmd "
RRECOMMENDS:${PN}:remove  = " packagegroup-base-apm apm apmd "
```

> 注意：`packagegroup-base-apm` 不是独立 recipe，清理/重编目标应为 `packagegroup-base`。

3. 设定 **SysVinit** 为唯一 PID1：

```text
VIRTUAL-RUNTIME_init_manager = "sysvinit"
VIRTUAL-RUNTIME_initscripts  = "initscripts"
BAD_RECOMMENDATIONS         += " busybox-inittab "
# 可加保险（可选）
RDEPENDS:busybox:remove     = " busybox-inittab "
RRECOMMENDS:busybox:remove  = " busybox-inittab "
```

### 4.2 解决 rcS 文件冲突（关键）

给 busybox 写 `bbappend`，**从源头不打出 rcS 两个文件**，并确保优先级覆盖发行层的同名 `bbappend`。

1. `busybox bbappend`：

```
meta-phytium/recipes-core/busybox/busybox_%.bbappend
```

```text
FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

do_install:append() {
    rm -f ${D}${sysconfdir}/init.d/rcS || true
    rm -f ${D}${sysconfdir}/default/rcS || true
}

FILES:${PN}:remove = " ${sysconfdir}/init.d/rcS ${sysconfdir}/default/rcS "
```

2. 确保 **BSP 层优先级更高**（让这份 bbappend 最终生效）：

```
meta-phytium/conf/layer.conf
```

```text
BBFILE_PRIORITY_meta-phytium = "60"
```

### 4.3 重建与自检

```bash
# 清理并重编包组/关键包
bitbake -c cleanall packagegroup-base busybox sysvinit openeuler-image
bitbake packagegroup-base busybox sysvinit

# 依赖与内容验证
rpm -qp --requires tmp/deploy/rpm/*/packagegroup-base-*.rpm | grep -Ei 'apm|apmd' || echo "OK: no APM dep"
rpm -qlp tmp/deploy/rpm/*/busybox-*.rpm | grep -E '/etc/(default/rcS|init\.d/rcS)' || echo "OK: busybox no rcS"

# 构建镜像（先普通，再有需要时构建 live）
bitbake openeuler-image
# 可选：bitbake openeuler-image-live
```

---

## 5. 解决方案（部署侧）

### 5.1 双分区更新（从 p1 更新 p2）

1. 校验并**完整解包**到 p2（保留属主/权限/xattrs）：

```bash
mount /dev/nvme0n1p2 /mnt/p2
sha256sum -c openeuler-image-phytium.tar.bz2.sha256
cd /mnt/p2
# 清空旧根后解包
find . -mindepth 1 -maxdepth 1 -xdev \
  ! -name 'openeuler-image-phytium.tar.bz2' ! -name '*.sha256' -exec rm -rf {} +
tar --xattrs --xattrs-include='*' --numeric-owner -xpf openeuler-image-phytium.tar.bz2 -C /mnt/p2
sync
```

2. 最小体检：

```bash
test -x /mnt/p2/sbin/init
file /mnt/p2/usr/lib64/libtirpc.so.3
```

3. 切换启动项指向 `root=/dev/nvme0n1p2`，必要时更新 `/boot` 中的 `Image`/`*.dtb`。

> 若仍担心“半写”，推荐直接用 `.ext4/.wic` 镜像 `dd` 到 `p2`，写完 `fsck.ext4 -f`。

---

## 6. 验证清单（构建+运行）

**构建期**

* `bitbake -e packagegroup-base | grep -E 'RDE|RRE.*packagegroup-base'` 不含 `apm/apmd`
* `rpm -qlp busybox-*.rpm` 不含 `/etc/init.d/rcS`、`/etc/default/rcS`
* `bitbake -g openeuler-image && ! grep -i busybox-inittab pn-buildlist`

**运行期（p2 启动后）**

```bash
ps -p 1 -o pid,comm,args       # PID1 为 /sbin/init（SysVinit），非 systemd
rpm -qa | grep -i '^apm' || echo "OK: no apm/apmd"
ldd /sbin/init | head -n 20    # 依赖库可解析
```

---

## 7. 经验与教训

1. **APM 是 x86 旧技术**：在 ARM64 上移除它完全合理，需同步处理 `packagegroup` 依赖与 `DISTRO_FEATURES`。
2. **panic 与 APM 无关**：报 `file too short` 基本是**根文件系统损坏或解包不完整**，首先检查解包参数/空间/`fsck`/或改用
   `.ext4` 直写。
3. **init 体系要唯一**：选了 SysVinit，就要**禁止 busybox 的 inittab 和 rcS 文件**，否则与 `sysvinit` 冲突。
4. **bbappend 的优先级**至关重要：同名 `bbappend` 多份都生效，最终以层优先级/应用顺序为准；必要时提高 BSP 层优先级或
   `BBMASK` 屏蔽发行层的 append。
5. **每次修改后都要重打相关 RPM 并用 `rpm -q{l,p} / -qp --requires` 验证**，不要只看配方。

---

## 8. 结论

通过：

* 移除 `apm` 发行特性并切断 `packagegroup-base` 的 APM 依赖；
* 确定 SysVinit 为唯一 init 管理器；
* 用 `busybox_%.bbappend` 从源头剔除 rcS 脚本并提升 BSP 层优先级；
* 部署侧使用正确、稳健的解包/写盘流程；

我们稳定地去除了 APM，解决了构建期的 dnf 冲突与运行期的启动异常，镜像可在 `nvme0n1p2` 正常启动。

