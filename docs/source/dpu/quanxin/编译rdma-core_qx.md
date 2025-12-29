# 编译 rdma-core_qx

## 目标

在商用开发板（openEuler Server 用户态）上，从 `rdma-core_qx` 源码 **编译成功**，暂时不集成进你的 rootfs，也不强制
`make install`。

---

## 0. 进入环境、准备源码目录

从服务器下载源码

```shell
wget http://rocky-server/618_projects/rdma-core_qx-master.tar.gz
```

将 `rdma-core_qx-master.tar.gz` 使用 U 盘复制到集特开发板上

假设现在文件 `rdma-core_qx-master.tar.gz` 已经复制到了 U 盘中。
启动开发板之后，登录系统，插入 U 盘。

查看块设备：

```text
lsblk
```

可以看到U 盘分区，假设 U 盘分区是 /dev/sda1，你可以挂载它到 /mnt

```sh
mount /dev/sda1 /mnt/
```

复制文件到 `/root`

```text
cd /mnt;
cp -v rdma-core_qx-master.tar.gz /root
```

复制完之后确认 `rdma-core_qx-master.tar.gz` 已经到 `/root` 目录了：

```text
ls -l /root
```

如果文件没问题，卸载 U 盘

```text
umount /dev/sda1
```

解压：

```shell
tar -xf rdma-core_qx-master.tar.gz
```

改下目录名

```shell
mv rdma-core_qx-master rdma-core_qx
```

假设你把目录放在：

```bash
SRC=/root/rdma-core_qx   # 或者你实际路径
cd $SRC
```

确认源码目录里有 `build.sh`、`CMakeLists.txt`。

---

## 1. 先清理厂商包自带的 build（必须做）

因为源码包里自带 `build/`，其中 `CMakeCache.txt` 记录了对方机器的绝对路径，换环境必报错。

直接清理：

```bash
cd $SRC
rm -rf build
```

---

## 2. 安装最小构建依赖

你在 chroot 里已经验证过：缺的是 `libnl3-devel`（提供 `pkgconfig(libnl-3.0)` 和 `pkgconfig(libnl-route-3.0)`）。

建议一次装齐最小工具链 + libnl：

```bash
dnf install -y gcc gcc-c++ make cmake pkgconf-pkg-config libnl3-devel
```

在无网条件下使用本地 yum 源安装工具依赖

```bash
dnf --disablerepo="*" --enablerepo="oe-local" install -y \
    gcc gcc-c++ make cmake pkgconf-pkg-config libnl3-devel
```

如果你的板子系统没有 `dnf` 源或者 everything 源没配好，这一步会卡；先把源配好再继续。

---

## 3. 禁用 man pages（必须做）

你已经确认源码里缺文件：
`infiniband-diags/man/common/opt_d.rst` 不存在，所以默认文档生成链路会炸。

项目提供开关 `NO_MAN_PAGES`，你之前 grep 出来了，且 build.sh 支持用 `EXTRA_CMAKE_FLAGS` 透传给 cmake

照抄：

```bash
cd $SRC
rm -rf build
EXTRA_CMAKE_FLAGS="-DNO_MAN_PAGES=1" ./build.sh
```

说明：

* 这一步会在 `$SRC/build/` 里生成构建产物，并编译出库和工具。
* `NO_MAN_PAGES=1` 的意义是“不要 build/install man pages”。

---

## 4. 构建产物在哪里、你主要关心哪些

在你这次 chroot 的构建结果里，动态库清单是这些（明天板子上也应该类似）：

* `./build/lib/libibverbs.so.1.14.37.0`
* `./build/lib/librdmacm.so.1.3.37.0`
* `./build/lib/libibumad.so.3.2.37.0`
* `./build/lib/libibmad.so.5.3.37.0`
* `./build/lib/libibnetdisc.so.5.0.37.0`
* 还有一些“provider/软 RDMA/示例相关”的 `.so`（比如 rxe/siw/hfi1verbs 等）

可执行工具在 `./build/bin/` 下非常多，你这次生成的包括：`ibv_devinfo`、`ibv_devices`、`rping`、`ibstat`、`perfquery`、
`srp_daemon` 等。

明天你最该关注的工具是：

* `./build/bin/ibv_devices`
* `./build/bin/ibv_devinfo`
* （如果你要看 RDMA CM）`./build/bin/rping`

---

## 5. 不安装也能做的快速自检（建议）

你今天的目标是不安装，所以明天你可以用 **临时 LD_LIBRARY_PATH** 直接运行 build 出来的工具，验证它们能起来：

```bash
cd $SRC
export LD_LIBRARY_PATH=$PWD/build/lib:$LD_LIBRARY_PATH

./build/bin/ibv_devices || true
./build/bin/ibv_devinfo || true
```

如果板子上内核/驱动/设备没就绪，这俩可能会输出 “No devices found” 或报权限/驱动相关错误，但至少你能确认用户态二进制能运行、动态链接没问题。

---

## 6. 可选：等你确定要装到板子系统时再做 install

等你后面真的要让板子系统“默认可用”（不靠 LD_LIBRARY_PATH）再：

```bash
cd $SRC/build
make install
ldconfig
```

但你现在说“内核还没弄完”，我同意先别 install，避免污染系统环境，后面排查会更乱。

---

## 7. 你这次构建已经证明的事实

* 这个厂商包 **不是完整的文档源包**：缺 `opt_d.rst`，所以默认 man pages 必炸。
* 只要禁用 man pages，核心库 + 工具链能正常编译。
* 最关键的依赖之一是 `libnl3-devel`，否则 cmake 配置阶段会直接失败。
