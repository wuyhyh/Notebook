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

#### 2.1.1 安装指定版本的 wsl

```text
wsl --list --online
wsl --list --online FedoraLinux-42
wsl --list --online Ubuntu-24.04
```

在根目录创建与 windows 文件系统的关联

```text
cd ~
echo 'export wuyh=/mnt/c/Users/wuyuhang/Downloads' >> .bashrc
source .bashrc
```

这样可以快速在两个文件系统之间切换。

#### 2.1.2 文件系统权限问题

由于 WSL 和 Windows 文件系统之间的权限模型不同，导致在 `/mnt/c/` 等挂载点下的文件权限显示异常。

- WSL 通过 `DrvFs` 文件系统访问 Windows 文件
- Windows 文件系统没有 Linux 风格的权限位
- WSL 为所有文件设置了默认权限（通常是 755）

**修改 WSL 配置文件**

编辑 `/etc/wsl.conf`：

```bash
sudo vim /etc/wsl.conf
```

添加以下内容：

```text
[automount]
enabled = true
options = "metadata,umask=022"
mountFsTab = false

[interop]
enabled = true
appendWindowsPath = true
```

**重启 WSL** 使配置生效（关闭所有 WSL 窗口重新打开）。

```text
wsl --shutdown
```

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

在 Git Bash 中，当文件名包含中文时，可能会显示为八进制转义序列。以下是解决方案：

```bash
# 设置 Git 使用 UTF-8 编码显示文件名
git config --global core.quotepath false

# 设置 Git 使用 UTF-8 编码处理文件名
git config --global i18n.logoutputencoding utf8
git config --global i18n.commitencoding utf8
```

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

### 2.5 在开发板上通过 SSH/SCP 直接访问 WSL

嵌入式开发板直接用 `ssh/scp` 访问 WSL 的 Linux 路径，不再经过Windows 用户目录或盘符路径。默认目标端口使用 **2223**，避免与
Windows 自身的 OpenSSH（22）冲突。

---

#### 2.5.1 前置条件

* Windows 10/11 + **WSL2（推荐商店版，`wsl --version` 可见版本号）**
* 开发板网络可达 Windows 主机的局域网 IP（示例：`192.168.11.100`）
* 开发板端 `scp` 若是 Dropbear，**后续命令都需要 `-O`**（legacy scp）

---

#### 2.5.2 把 WSL 放到与局域网同一网段（mirrored）

1）管理员 PowerShell：

```powershell
wsl --version              # 建议为商店版，能看到“WSL version: x.y.z”；低版本先 wsl --update
wsl --shutdown             # 关闭所有 WSL 实例
```

2）创建/编辑 `C:\Users\<你>\.wslconfig`：

```powershell
[wsl2]
networkingMode=mirrored
dnsTunneling=true
autoProxy=true
```

3）重新进入 WSL：

```powershell
wsl
```

4）在 WSL 内确认（应见到一个与主机同网段/或共享主机 IP 的接口，如 `192.168.11.100/24`）：

```bash
ip a
```

---

#### 2.5.3 在 WSL 中部署并启动 `sshd`（监听 2223）

1）安装与准备：

```bash
sudo apt update
sudo apt install -y openssh-server
sudo ssh-keygen -A                 # 生成主机密钥
sudo mkdir -p /run/sshd && sudo chmod 0755 /run/sshd
```

2）配置 `sshd`（绑定到所有 IPv4 地址，并使用 2223 端口）：

```bash
# 修改/追加关键项
sudo sed -i 's/^#\?Port .*/Port 2223/' /etc/ssh/sshd_config
grep -q '^AddressFamily' /etc/ssh/sshd_config || echo 'AddressFamily inet' | sudo tee -a /etc/ssh/sshd_config
grep -q '^ListenAddress'  /etc/ssh/sshd_config || echo 'ListenAddress 0.0.0.0' | sudo tee -a /etc/ssh/sshd_config

# 如需口令登录（可选，便于临时使用）
sudo sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config
passwd    # 设定 WSL 用户密码（首次需要）
```

3）先**直接后台拉起**一个 `sshd`（不依赖 systemd，便于立即验证）：

```bash
sudo pkill -f "/usr/sbin/sshd.*2223" 2>/dev/null || true
sudo /usr/sbin/sshd -E /var/log/sshd-2223.log -D -p 2223 -o ListenAddress=0.0.0.0 &
sleep 1
ss -lntp | grep 2223      # 看到 0.0.0.0:2223 处于 LISTEN 即可
```

> 日志可查看：`sudo tail -f /var/log/sshd-2223.log`

---

#### 2.5.4 Windows 防火墙放行 2223（仅放行，不要让 Windows 占用端口）

管理员 PowerShell：

```powershell
netsh advfirewall firewall add rule name="WSL-SSH-2223" dir=in action=allow protocol=TCP localport=2223 profile=private
# 验证：最好看不到任何进程在 2223 上监听（表示没被 Windows 抢占）
Get-NetTCPConnection -LocalPort 2223 -State Listen
```

> 若这里显示有监听者，说明被 Windows 进程占用；请确认**未**启动 Windows 的 sshd 或其它服务在 2223 监听。

---

#### 2.5.5 连通性自检

1）**在 Windows 本机测试**（确保链路到达 WSL，而非 Windows 自身）：

```powershell
ssh -p 2223 <wsl_user>@127.0.0.1
# 能进 WSL shell 即通过
```

2）**从开发板测试**：

```sh
# 登录
ssh -p 2223 <wsl_user>@192.168.11.100

# 复制（Dropbear 的 scp 必须加 -O）
scp -O -P 2223 <wsl_user>@192.168.11.100:~/file.img /mnt/p2/
```

---

#### 2.5.6 启用 systemd，让 sshd 自启动(可选)

如果你希望 WSL 每次启动自动运行 `sshd`：

1）在 WSL：启用 systemd

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
```

2）在 Windows 执行：

```powershell
wsl --shutdown
```

3）回到 WSL：

```bash
sudo systemctl enable --now ssh
systemctl status ssh
```

> 启用 systemd 后，**端口仍然建议用 2223**（避免 Windows 22 端口冲突）。若要改用 22，请先停用并禁用 Windows 的 `sshd` 服务。











