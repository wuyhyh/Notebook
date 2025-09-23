# Git 本地仓库和内网服务器的部署

当我们的代码不能发布到 github 上的时候，我们需要在本地机器上部署本地远程仓库作为代码副本。
或者在内网服务器中部署一个仓库，这样方便多人进行简单的协作开发。

下面在 Windows 上如何通过 **本地裸仓库**、**Fedora Server 远程仓库（物理机）** 和 **Fedora Server 远程仓库（虚拟机 NAT +
端口转发）** 实现多人协作与备份的方案，并介绍了 SSH 免密登录的配置方法。

---

## 一、本地裸仓库方案

适用于：

* 单机开发但需要仓库备份；
* 不希望项目数据托管到外部平台（如 GitHub、GitLab）；
* 本机磁盘有额外空间可用。

### 1. 创建裸仓库

在 git bash 中执行创建仓库的命令

```bash
mkdir -p /c/Users/wuyuhang/git-backups
git init --bare /c/Users/wuyuhang/git-backups/my_project.git
```

### 2. 在项目中添加远程并推送

同样在 git bash 中执行这些命令

```bash
cd /c/Users/wuyuhang/CLionProjects/my_project
git remote add backup /c/Users/wuyuhang/git-backups/my_project.git
git push backup --all
git push backup --tags
```

> 注意: 如果项目是在 WSL 中进行开发，你希望 C 盘中的某个目录作为项目仓库，应该增加 `/mnt` 前缀在盘符前面
> ```text
> git remote add backup /mnt/c/Users/wuyuhang/git-backups/my_project.git
> ```

### 3. 从备份恢复

同样在 git bash 中执行这些命令

```bash
git clone /c/Users/wuyuhang/git-backups/my_project.git /c/Users/wuyuhang/CLionProjects/my_project
```

### 4. 远程仓库变更

当远程仓库的 IP 地址发生变化之后，需要修改 URL

```text
git remote set-url <remote-name> <new-url>
```

完全不再跟踪远程仓库（删除 remote）

```text
git remote remove <remote-name>
```

添加一个新的远程仓库

```text
git remote add <remote-name> <url>
```

为已存在的本地分支设置要跟踪的远程仓库

```text
git branch --set-upstream-to origin/<remote-branch-name> <local-branch-name>
```

---

## 二、远程仓库（Fedora Server 物理机）

适用于：

* 多人协作开发；
* 局域网内多台 Windows 主机共享同一个 Linux 服务器中的远程 Git 仓库。

### 1. 网络配置

* Fedora Server 与开发所用的 Windows PC 有相同网段的 IP，例如：

    * PC1：`172.16.21.119`
    * PC2：`172.16.21.99`
    * Fedora Server：`172.16.21.150`

### 2. Fedora 创建远程仓库

```bash
sudo dnf install -y git
sudo useradd git
sudo passwd git
sudo mkdir -p /srv/git
sudo chown git:git /srv/git
sudo -u git git init --bare /srv/git/project.git
```

### 3. 启用 SSH 服务

```bash
sudo systemctl enable --now sshd
```

### 4. Windows 添加远程并推送

```bash
git clone ssh://git@172.16.21.150/srv/git/project.git
# 或
git remote add origin ssh://git@172.16.21.150/srv/git/project.git
git push -u origin master
```

---

## 三、远程仓库（Fedora Server NAT + 端口转发）

适用于：

* VMware 使用 **NAT 网络**，虚拟机只有私有地址（如 `192.168.79.128`）；
* 希望宿主机与局域网内其他主机（同事电脑）也能访问该仓库。

### 1. 配置 VMware NAT 端口转发

> 配置端口转发也可以在 VMware 虚拟网络配置中图形化配置
> 重点是建立端口映射 22 -> 2222

* 编辑 VMware 的 `vmnetnat.conf`（Windows 路径通常为 `C:\ProgramData\VMware\` 下）。
* 在 `[incomingtcp]` 部分添加规则，将宿主机的端口转发到虚拟机的 SSH：

  ```
  2222 = 192.168.79.128:22
  ```
* 重启 VMware NAT 服务：

  ```powershell
  net stop "VMware NAT Service"
  net start "VMware NAT Service"
  ```

### 2. Windows 访问仓库

使用宿主机 IP（例如 `172.16.21.119`）加转发端口：

```bash
git clone ssh://git@172.16.21.119:2222/srv/git/project.git
# 或
git remote add origin ssh://git@172.16.21.119:2222/srv/git/project.git
git push -u origin master
```

### 3. 同事访问

同事机器使用宿主机的公网地址（`172.16.21.119:2222`）即可访问 Fedora 虚拟机仓库。

---

## 四、免密登录配置

### 1. Windows 生成 SSH 密钥

```bash
ssh-keygen
```

* 默认生成在 `~/.ssh/id_rsa` 和 `~/.ssh/id_rsa.pub`。
* 保留私钥 `id_rsa`，把公钥 `id_rsa.pub` 上传到服务器。

### 2. 将公钥添加到 Fedora

在 Windows 上查看公钥：

```bash
cat ~/.ssh/id_rsa.pub
```

> 生成公钥之后可以直接在 Git bash 中执行命令：
> ```bash
> ssh-copy-id -p 2222 git@172.16.21.119
> ```

或者复制后，在 Fedora 登录 `git` 用户，执行：

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. 测试免密登录

```bash
ssh -p 2222 git@172.16.21.119   # NAT 模式
ssh git@172.16.21.150           # 物理机模式
```

### 4. 从服务器 clone 代码

之后可直接使用：

```bash
git clone fedora-git:/srv/git/project.git
```
