# Rocky Linux 10（el10）+ GitLab CE Omnibus RPM 的标准流程

我按 Rocky 10 / GitLab CE Omnibus 的标准流程，把从安装 rpm、写 external_url、开防火墙、初始化到验证访问的命令一条条给你，避免你再踩
https/HSTS 的坑。

下面按 Rocky Linux 10（el10）+ GitLab CE Omnibus RPM 的标准流程给你一套“照抄就能装起来”的命令序列。你已经有
`gitlab-ce-18.6.2-ce.0.el10.x86_64.rpm`，我默认你要用 **HTTP**（避免你之前的 https/HSTS 坑），域名用你定的
`rocky-server.lab`，IP 固定 `192.168.1.102`。

---

## 0. 前置：主机名与 hosts（在 i5 上）

```bash
sudo hostnamectl set-hostname rocky-server
echo "192.168.1.102 rocky-server.lab rocky-server" | sudo tee -a /etc/hosts
```

确认：

```bash
hostname
getent hosts rocky-server.lab
```

---

## 1. 基础依赖与时钟

```bash
sudo dnf -y update
sudo dnf -y install curl policycoreutils openssh-server perl
sudo systemctl enable --now sshd
sudo timedatectl set-timezone Asia/Shanghai
```

---

## 2. 安装你下载的 GitLab RPM

假设 rpm 在当前目录：

```bash
sudo dnf -y install ./gitlab-ce-18.6.2-ce.0.el10.x86_64.rpm
```

如果你是在离线环境，dnf 可能提示缺依赖；那就把依赖包也准备好。正常联网的话一般能自动拉齐依赖。

---

## 3. 写 external_url（强制 HTTP，避免 https/HSTS）

```text
vim /etc/gitlab/gitlab.rb
```

```text
external_url 'http://rocky-server.lab'
```

UI 展示的 SSH clone 主机名

```text
gitlab_rails['gitlab_ssh_host'] = 'rocky-server.lab'
```

---

## 4. 初始化配置并启动

```bash
sudo gitlab-ctl reconfigure
sudo gitlab-ctl restart
sudo gitlab-ctl status
```

---

## 5. 防火墙放行（HTTP + SSH）

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

---

## 6. 验证（在 i5 上）

### 6.1 Nginx 配置里是否是新域名

```bash
sudo grep -R "server_name" -n /var/opt/gitlab/nginx/conf | head -n 20
```

---

## 7. 初始 root 密码

首次安装后，root 初始密码通常在：

```bash
sudo cat /etc/gitlab/initial_root_password
```

注意：这个文件会在一段时间后被 GitLab 删除（或你重配后变化），看到就立刻保存。

---

## 8. 客户端（Windows/WSL）侧 hosts

在浏览器那台机器上也要加：

```
192.168.1.102  rocky-server.lab rocky-server
```

然后清 DNS 缓存：

* Windows（管理员 PowerShell）：

```powershell
ipconfig /flushdns
```

