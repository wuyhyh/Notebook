非常好，这是深入理解 Fedora（或任何 RPM 系发行版）软件打包机制的最佳起点！

下面我会带你从零开始，创建一个简单的 `HelloWorld` 程序，然后打包成 `.rpm` 格式，并可安装、卸载。

---

# ✅ 目标：打包一个 `hello` 程序（打印 "Hello, RPM World!"）

---

## 📦 一、准备环境（首次打包才需）

```bash
sudo dnf install rpm-build rpmdevtools gcc make
rpmdev-setuptree
```

该命令会在 `$HOME` 下创建如下目录：

```bash
~/rpmbuild/
├── BUILD
├── BUILDROOT
├── RPMS
├── SOURCES
├── SPECS
└── SRPMS
```

---

## 🧾 二、准备源码和构建脚本

### 1. 创建 C 源码文件：

```bash
mkdir -p ~/rpmbuild/SOURCES/hello-1.0
cd ~/rpmbuild/SOURCES/hello-1.0
```

创建 `hello.c`：

```c
#include <stdio.h>

int main() {
    printf("Hello, RPM World!\n");
    return 0;
}
```

创建 `Makefile`：

```makefile
CC = gcc
CFLAGS = -Wall -O2

all: hello

hello: hello.c
	$(CC) $(CFLAGS) -o hello hello.c

install:
	mkdir -p $(DESTDIR)/usr/bin
	cp hello $(DESTDIR)/usr/bin/

clean:
	rm -f hello
```

打包源码 tarball：

```bash
cd ~/rpmbuild/SOURCES
tar -czf hello-1.0.tar.gz hello-1.0
```

---

## 🧾 三、编写 `.spec` 文件

```bash
cd ~/rpmbuild/SPECS
nano hello.spec
```

填入以下内容（解释见后）：

```spec
Name:           hello
Version:        1.0
Release:        1%{?dist}
Summary:        A simple HelloWorld RPM example

License:        MIT
URL:            https://example.com
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  gcc, make

%description
This is a simple example RPM package that prints "Hello, RPM World!"

%prep
%autosetup

%build
make

%install
make install DESTDIR=%{buildroot}

%files
%license
/usr/bin/hello

%changelog
* Tue Aug 06 2025 吴宇航 <you@example.com> - 1.0-1
- Initial package
```

---

## 🛠 四、构建 RPM 包

```bash
rpmbuild -ba hello.spec
```

如果一切顺利，会看到：

```
Wrote: ~/rpmbuild/RPMS/x86_64/hello-1.0-1.fc42.x86_64.rpm
```

---

## 🧪 五、安装和测试

```bash
sudo dnf install ~/rpmbuild/RPMS/x86_64/hello-1.0-1.fc42.x86_64.rpm
hello
# 输出: Hello, RPM World!
```

---

## 🧹 六、卸载包

```bash
sudo dnf remove hello
```

---

## 📌 `.spec` 文件说明

| 字段                           | 含义                        |
|------------------------------|---------------------------|
| `Name`, `Version`, `Release` | 定义包名/版本                   |
| `Source0`                    | 指定源码压缩包                   |
| `%prep`                      | 解压和打补丁（`%autosetup` 自动处理） |
| `%build`, `%install`         | 构建和安装逻辑                   |
| `%files`                     | 指定最终安装路径文件列表              |
| `%changelog`                 | 可选的维护日志                   |

---

## ✅ 总结命令清单（你可以直接复制执行）

```bash
sudo dnf install rpm-build rpmdevtools gcc make
rpmdev-setuptree

cd ~/rpmbuild/SOURCES
mkdir hello-1.0 && cd hello-1.0
# 创建 hello.c 和 Makefile
cd ..
tar -czf hello-1.0.tar.gz hello-1.0

cd ~/rpmbuild/SPECS
# 创建 hello.spec 文件

rpmbuild -ba hello.spec
sudo dnf install ~/rpmbuild/RPMS/x86_64/hello-1.0-1.fc*.rpm
hello
```

---

是否希望我为你生成一个完整的 `.spec` 模板或者是更复杂的案例（比如带配置文件、systemd 服务的 RPM）？

