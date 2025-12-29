# 双 GitLab 连续工作流规范

## 1. 目标与约束

1. 公司 i5 的 GitLab 是唯一权威仓库（团队协作入口），维护稳定的 `master`。
2. 个人开发永远在个人分支上进行（本文以 `wuyuhang/dev` 为例）。
3. 家里无法访问公司 i5；家里只有 tokamak-4 的 GitLab 可用。
4. 公司内团队成员只访问公司 i5，不访问 tokamak-4。
5. tokamak-4 作为“移动中转站”，负责把家里的个人分支带到公司，并把公司 `master` 带回家。

---

## 2. 网络与域名约定

### 家里

- GitLab 主机：`tokamak-4`（Rocky Server）
- GitLab external_url：`http://tokamak-4.home`
- hosts 映射（tokamak-4 本机）：
    - `tokamak-4.home -> 127.0.0.1`（本机自用，最稳）
- SSH 地址（家里 GitLab）：
    - `git@tokamak-4.home:618_projects/hpc_project.git`

### 公司

- GitLab 主机：`rocky-server`（i5，固定 IP）
- hosts 映射（公司内所有客户端）：
    - `rocky-server.lab -> 192.168.1.102`
- SSH 地址（公司 GitLab）：
    - `git@rocky-server.lab:618_projects/hpc_project.git`

---

## 3. 工具：跨平台 hosts 脚本

使用 `setup_hosts_xplat.py`（Windows/WSL/macOS/Linux 通用）更新 hosts。

### Linux / Rocky / WSL / macOS（改 /etc/hosts）

```bash
sudo python3 setup_hosts_xplat.py --ip 192.168.1.102 --host rocky-server.lab
```

```bash
sudo python3 setup_hosts_xplat.py --ip 127.0.0.1 --host tokamak-4.home
```

### Windows（管理员 PowerShell，改 Windows hosts；默认同步 WSL）

```powershell
python setup_hosts_xplat.py --ip 192.168.1.102 --host rocky-server.lab
```

```powershell
python setup_hosts_xplat.py --ip 192.168.1.7   --host tokamak-4.home
```

---

## 4. 分支策略（必须遵守）

### 分支角色

* `master`：稳定分支，仅在公司 i5 上合并更新（MR 或 i5 命令行），其他地方禁止直接提交。
* `wuyuhang/dev`：个人长期开发分支（家/公司均在该分支开发、提交、推送）。

### 总原则

* **在家**：只 push 到 tokamak-4（home）。
* **在公司**：只 push 到 i5（lab）。
* **合并到 master**：只在 i5 完成。

---

## 5. Remote 约定

在 tokamak-4 的工作副本（`/home/wuyuhang/HPC_project`）配置两个 remote：

* `home`：家里 GitLab
* `lab`：公司 GitLab（i5）

示例（tokamak-4 上）：

```bash
git remote add home git@tokamak-4.home:618_projects/hpc_project.git
git remote add lab git@rocky-server.lab:618_projects/hpc_project.git
```

检查：

```bash
git remote -v
```

---

## 6. 日常流程

### A. 在家（Tokamak-1 开发 → 推到 tokamak-4）

1. 在 Tokamak-1 使用个人分支开发：

```bash
git checkout wuyuhang/dev
# 开发、commit...
git commit -am "xxx"
```

2. 推到家里 GitLab（tokamak-4）：

```bash
git push origin wuyuhang/dev
```

> 说明：Tokamak-1 的 `origin` 应指向 `tokamak-4.home`。

---

### B. 到公司（tokamak-4 搬运 dev → 推到 i5）

tokamak-4 带到公司网络后，在 tokamak-4 的工作副本执行：

```bash
cd /home/wuyuhang/HPC_project
git fetch home
git push lab wuyuhang/dev
```

---

### C. 在公司（Tokamak-2 开发 → 直接推 i5）

在 Tokamak-2 的仓库中：

1. 确保在 `wuyuhang/dev`：

```bash
git checkout wuyuhang/dev || git checkout -b wuyuhang/dev
```

2. 同步 i5 上该分支最新提交：

```bash
git pull --rebase origin wuyuhang/dev
# 或者：git pull --rebase lab wuyuhang/dev（取决于 remote 名字）
```

3. 开发并推到 i5：

```bash
git commit -am "xxx"
git push origin wuyuhang/dev
```

> 注意：公司侧只认 i5（lab/origin），不要推 home。

---

### D. 合并到 master（只在 i5 做）

在 i5 的 GitLab 上创建 Merge Request：

* Source: `wuyuhang/dev`
* Target: `master`

合并完成后，`master` 才算更新。

---

### E. 下班前：把公司 master 带回家（i5 → tokamak-4 → Tokamak-1）

在 tokamak-4 的工作副本执行：

```bash
cd /home/wuyuhang/HPC_project

# 从 i5 拉 master
git fetch lab
git checkout master
git pull --rebase lab master

# 推回家里 GitLab（tokamak-4）
git push home master
```

回家后 Tokamak-1 从 tokamak-4 拉 `master`：

```bash
git checkout master
git pull --rebase origin master
```

---

## 7. 出差模式（tokamak-4 切 Windows，不跑 GitLab）

1. 以公司 i5 为唯一上游（只要能访问到 i5 就 clone）：

```bash
git clone git@rocky-server.lab:618_projects/hpc_project.git
git checkout -b wuyuhang/dev origin/wuyuhang/dev
```

2. 出差期间只 commit，不 push（离线开发）：

```bash
git commit -am "xxx"
```

3. 回到能访问 i5 的网络环境后再 push：

```bash
git push origin wuyuhang/dev
```

---

## 8. 最常见错误与规避

1. **在 tokamak-4 或 Tokamak-1 上直接改 `master`**

* 规避：所有开发只在 `wuyuhang/dev`，`master` 只在 i5 合并后更新。

2. **remote 搞混（推错仓库）**

* 规避：tokamak-4 上固定两 remote：`home` / `lab`；公司侧只用 i5 的 `origin`。

3. **tokamak-4 工作副本缺少 `wuyuhang/dev`**

* 处理：

```bash
git fetch home
git checkout -b wuyuhang/dev home/wuyuhuhang/dev
```

（或按实际远端分支名创建跟踪分支）

---

## 9. 快速检查清单（每天 30 秒）

在家（Tokamak-1）：

* `git branch` 是否在 `wuyuhang/dev`
* `git remote -v` 是否指向 `tokamak-4.home`

在公司（Tokamak-2）：

* `git branch` 是否在 `wuyuhang/dev`
* push 是否只到 i5（`rocky-server.lab`）

tokamak-4（中转）：

* `git push lab wuyuhang/dev` 是否成功
* `git pull --rebase lab master` 是否成功
* `git push home master` 是否成功
