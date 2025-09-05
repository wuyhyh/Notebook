# LFS 安装基本系统软件 Part3

## 51. Wheel-0.45.1

Wheel 是 Python wheel 软件包标准格式的参考实现。

```text
cd /sources;tar -xf wheel-0.45.1.tar.gz;cd wheel-0.45.1
```

执行以下命令编译 Wheel：

```text
pip3 wheel -w dist --no-cache-dir --no-build-isolation --no-deps $PWD
```

使用以下命令安装 Wheel：

```text
pip3 install --no-index --find-links dist wheel
```

## 52. Setuptools-75.8.1

Setuptools 是一个用于下载、构建、安装、升级，以及卸载 Python 软件包的工具。

```text
cd /sources;tar -xf setuptools-75.8.1.tar.gz;cd setuptools-75.8.1
```

构建该软件包：

```text
pip3 wheel -w dist --no-cache-dir --no-build-isolation --no-deps $PWD
```

安装该软件包：

```text
pip3 install --no-index --find-links dist setuptools
```

## 53. Ninja-1.12.1

Ninja 是一个注重速度的小型构建系统。

```text
cd /sources;tar -xf ninja-1.12.1.tar.gz;cd ninja-1.12.1
```

可通过一个环境变量 NINJAJOBS 限制并行进程数量。例如设置：

```text
export NINJAJOBS=4
```

会限制 ninja 使用 4 个并行进程。

如果希望 ninja 能够识别环境变量 NINJAJOBS，使用流编辑器，添加这一功能：

```text
sed -i '/int Guess/a \
int   j = 0;\
char* jobs = getenv( "NINJAJOBS" );\
if ( jobs != NULL ) j = atoi( jobs );\
if ( j > 0 ) return j;\
' src/ninja.cc
```

构建 Ninja：

```text
python3 configure.py --bootstrap --verbose
```

测试套件无法在 chroot 环境中运行。它需要 cmake。
不过，重新构建该软件包本身 (由 --bootstrap 选项要求) 已经测试了它的基本功能。

安装该软件包：

```text
install -vm755 ninja /usr/bin/
install -vDm644 misc/bash-completion /usr/share/bash-completion/completions/ninja
install -vDm644 misc/zsh-completion  /usr/share/zsh/site-functions/_ninja
```

## 54. Meson-1.7.0

Meson 是一个开放源代码构建系统，它的设计保证了非常快的执行速度，和尽可能高的用户友好性。

```text
cd /sources;tar -xf meson-1.7.0.tar.gz;cd meson-1.7.0
```

执行以下命令编译 Meson：

```text
pip3 wheel -w dist --no-cache-dir --no-build-isolation --no-deps $PWD
```

测试套件需要一些超过 LFS 覆盖范围的软件包。

安装该软件包：

```text
pip3 install --no-index --find-links dist meson
install -vDm644 data/shell-completions/bash/meson /usr/share/bash-completion/completions/meson
install -vDm644 data/shell-completions/zsh/_meson /usr/share/zsh/site-functions/_meson
```

## 55. Kmod-34

Kmod 软件包包含用于加载内核模块的库和工具。

```text
cd /sources;tar -xf kmod-34.tar.xz;cd kmod-34
```

准备编译 Kmod：

```text
mkdir -p build
cd       build

meson setup --prefix=/usr ..    \
            --sbindir=/usr/sbin \
            --buildtype=release \
            -D manpages=false
```

编译该软件包：

```text
ninja
```

该软件包的测试套件需要内核的原始头文件 (不是之前安装的 “净化的” 内核头文件)，原始头文件超出了 LFS 的范畴。

现在安装该软件包：

```text
ninja install
```
