# 构建 U-Boot 二进制

U-Boot 是一个 C 语言为主的项目，使用make gcc 等工具链。
因为需要支持很多不同的 boards, 所以构建的时候需要生成配置文件。
整个过程和 Linux 内核构建是很相似的。

## 交叉编译

- Dependencies

For building U-Boot you need a GCC compiler for your host platform. If you are not building on the target platform you
further need a GCC cross compiler.

对于 Ubuntu:

```shell
sudo apt-get install gcc gcc-aarch64-linux-gnu
```

此外还需要一些构建工具

```shell
sudo apt-get install bc bison build-essential coccinelle \
  device-tree-compiler dfu-util efitools flex gdisk graphviz imagemagick \
  libgnutls28-dev libguestfs-tools libncurses-dev \
  libpython3-dev libsdl2-dev libssl-dev lz4 lzma lzma-alone openssl \
  pkg-config python3 python3-asteval python3-coverage python3-filelock \
  python3-pkg-resources python3-pycryptodome python3-pyelftools \
  python3-pytest python3-pytest-xdist python3-sphinxcontrib.apidoc \
  python3-sphinx-rtd-theme python3-subunit python3-testtools \
  python3-venv swig uuid-dev
```

- Configuration

一些 boards 需要进行配置

```shell
make odroid-c2_defconfig
```

还可以通过 menuconfig 进行个性化配置

```shell
make menuconfig
```

- 编译

```shell
CROSS_COMPILE=aarch64-linux-gnu- make -j${nproc}
```
