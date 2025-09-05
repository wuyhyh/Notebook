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


