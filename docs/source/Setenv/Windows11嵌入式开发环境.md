# Windows 11 嵌入式环境搭建

windows 系统在 amd64 机器上是比较稳定的，我们需要安装一些工具方便我们的开发工作。

## 1. 安装工具

### 1.1 chrome 浏览器

下载安装 [Chrome 浏览器](https://www.google.com/intl/zh-CN/chrome/)，使用 Google 账号登录，方便同步文件。

### 1.2 VPN 软件

- [pigcha](https://web.marslinkvpn.com/)
- [letsvpn](https://www.nletsb.com/)

### 1.3 截图软件

[snipaste](https://zh.snipaste.com/download.html)

### 1.4 终端软件

[MaboXterm](https://mobaxterm.mobatek.net/download.html)

### 1.5 虚拟机

安装完整的虚拟机管理器，现在已经完全免费，登录博通官网下载：

VMware Workstation

### 1.6 Adobe PDF reader

安装一个 PDF 阅读器，也是免费的。

### 1.7 解压缩工具

下载免费的 [7z](https://www.7-zip.org/)

我更喜欢使用 Git bash 中集成的 tar

压缩率高

```text
tar -cJf file.tar.xz file/
tar -xf file.tar.xz
```

通用性强

```text
tar -czf file.tar.gz file/
tar -zxf file.tar.gz
```

### 1.8 安装 CLion

CLion 用作底层软件开发是非常方便的。

我们可以使用 `bear` 生成编译数据库文件，并且配置 CLion 的工具链为 `wsl`，这样就能实现代码的索引，非常方便。

为了良好的 **coding style**，打开空白字符的显示选项。

## 2. 配置

### 2.1 安装 wsl

```text
wsl --list --online
wsl --list --online FedoraLinux-42
wsl --list --online Ubuntu-24.04
```

在根目录创建与 windows 文件系统的关联

```text
cd ~
echo 'export wuyh=/mnt/c/User/wuyuhang/Downloads' >> .bashrc
source .bashrc
```

这样可以快速在两个文件系统之间切换。

### 2.2 配置 Git

[Git](https://git-scm.com/install/windows) 是必须安装和配置的

```text
ssh-keygen
```

复制 `~/.ssh` 目录下的公钥到远端服务器，方便代码下载和托管。

```text
sudo apt install git -y
```

```text
sudo dnf install git -y
```

```text
git config --global user.name wuyhyh
git config --global user.email wuyhyh@gmail.com
git config --global core.editor vim
```

在 **windows** 下也应该安装 Git，Git bash 可以在windows上执行很多有用的命令。

在 windows 的 `User/wuyuhang` 根目录下也该生成 `ssh-keygen`，这样 windows 机器才会被远端仓库认识。

### 2.3 大模型

- 免费的 **deepseek** 豆包

- 记忆力很好的收费的 **ChatGPT**

### 2.4 恢复 Windows 11 右键完整菜单显示

使用文本编辑器创建 `right_click_config.bat` 文件

```text
@echo off
reg add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /ve /d "" /f
taskkill /f /im explorer.exe & start explorer.exe
echo Windows 11 右键菜单已恢复完整选项！
pause
```

右键以管理员身份运行

