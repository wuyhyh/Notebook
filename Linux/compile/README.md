# 编译 Linux 内核

## 内核源码的获取

- vanilla kernel

从 [kernel.org](https://www.kernel.org/) 下载的 Linux 主线内核源码，未经任何发行版修改

- Git

```shell
git clone https://github.com/torvalds/linux.git
```

这个文件非常大，只 clone 最新版的代码：

```bash
git clone https://github.com/torvalds/linux.git --depth=1
```

使用[清华的镜像源](https://mirrors.tuna.tsinghua.edu.cn/help/linux.git/)：

```shell
git clone https://mirrors.tuna.tsinghua.edu.cn/git/linux.git --depth=1
```

## 在 Fedora 上编译内核

- 安装工具

```bash
sudo dnf install ncurses-devel bison flex elfutils-libelf-devel openssl-devel \
  dwarves perl gcc make bc wget zstd xz
```

- 生成编译配置文件

```shell
make defconfig
```

使用tui图形界面选择编译的组件

```shell
make menuconfig
```

- 并行编译内核

```shell
make -j${nproc}
```

使用12个核心并行编译内核，记录编译时间并生成编译数据库

```shell
time bear -- make -j12
```

- 安装内核模块

```shell
make modules_install
```

- 安装内核

```shell
make install
```

- 清理编译产物，彻底清理生成的文件

```shell
make clean
make mrproper
```

## 在 Ubuntu 上编译内核




