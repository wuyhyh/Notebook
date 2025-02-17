# Zsh 及其配置

---

Linux 下有很多 Shell，最常见的是 Bash，此外还有 Zsh、csh、ksh。推荐使用 Zsh。

Zsh 有如下特点：

- 语法基本完全兼容于 Bash，一般用户完全体会不到其区别
- Zsh 提供命令补全特性，比 Bash 的补全要更好用
- 可配置性强

## 安装 Zsh

在终端键入 `zsh --version`，若显示 Zsh 版本号，则表示 Zsh
已安装。否则需要安装 Zsh。

自 macOS Catalina（10.15）开始，macOS 系统默认的 Shell 已由 Bash 变为 Zsh。

Linux 用户可以使用如下命令安装 Zsh：

fedora

```
$ sudo dnf install zsh
```

Ubuntu/Debian

```
$ sudo apt install zsh
```

通过如下命令设置默认 Shell 为 Zsh:

```
$ chsh -s $(which zsh)
```

`chsh` 命令修改的是登陆 Shell，因而需要退出当前用户并重新登陆，
用户的默认 Shell 就从 Bash 变成 Zsh 了。打开新的终端并键入
`echo $SHELL`，查看当前 Shell，会显示 {file}`/bin/zsh`。

若出现 `chsh: command not found` 错误，则需要安装 util-linux-user:

fedora

```
$ sudo dnf install util-linux-user
```

Zsh 的配置文件为 {file}`~/.zshrc`。因而切换到 Zsh 后，
所有的 Shell 配置都不用写到 {file}`~/.bashrc`，而要写到 {file}`~/.zshrc` 中。

## Oh My Zsh

Zsh 稍作配置会更加方便好用。[Oh My Zsh](https://ohmyz.sh/) 是由 Oh My Zsh 社区
维护的一套 Zsh 配置文件，使用起来非常方便。一般用户直接使用该配置即可。

安装 Oh My Zsh:

```
$ sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

该命令会创建 {file}`~/.oh-my-zsh` 目录，下载 Oh My Zsh 到该目录下，生成默认的 Zsh 配置文件
{file}`~/.zshrc`，并备份老的配置到类似 {file}`~/.zshrc.pre-oh-my-zsh` 的文件中。
