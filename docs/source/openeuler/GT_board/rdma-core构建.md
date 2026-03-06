# rdma-core 构建

> 在集特板上，从 `rdma-core_qx` 源码编译 RDMA 用户态库和驱动。
>
> 操作系统版本： openeuler server 2203 SP4，内核为 5.10.0-136.12.0.86.aarch64

---

## 0. 准备源码

从服务器下载源码

```shell
mkdir -p ~/src  && cd ~/src
git clone git clone git@rocky-server.lab:618_projects/rdma-core_qx.git
```

确认源码目录里有 `build.sh`、`CMakeLists.txt`。

---

## 1. 先清理厂商包自带的 build（必须做）

因为源码包里自带 `build/`，其中 `CMakeCache.txt` 记录了对方机器的绝对路径，换环境必报错。

直接清理：

```bash
SRC=$HOME/src/rdma-core_qx
cd $SRC
rm -rf build
```

---

## 2. 安装最小构建依赖

直接编译缺的是 `libnl3-devel`（提供 `pkgconfig(libnl-3.0)` 和 `pkgconfig(libnl-route-3.0)`）。

建议一次装齐最小工具链 + libnl：

```bash
dnf install -y gcc gcc-c++ make cmake pkgconf-pkg-config libnl3-devel
```

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

在你这次 chroot 的构建结果里，动态库清单是这些：

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
