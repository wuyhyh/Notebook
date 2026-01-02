# 启动阶段 daemon 裁剪

## 1. 精简 sshd（只保留客户端能力）

**目标**

* 启动阶段不再自动启动 SSH 服务器 `sshd`，减少启动耗时和无谓的后台进程。
* 仍然保留 `ssh/scp` 客户端功能，方便开发板主动连接 PC/服务器。

**现象**

* 启动时出现：

  ```text
  Starting OpenBSD Secure Shell server: sshd
    generating ssh RSA host key...
    generating ssh ECDSA host key...
    generating ssh ED25519 host key...
  ```

* 第一次启动会因为生成主机密钥明显拖慢启动；后续每次也会多一个常驻的 `sshd` 进程。

**分析**

* 系统使用 SysV init：

    * 服务脚本：`/etc/init.d/sshd`
    * 自启链接：`/etc/rc2.d/S09sshd`、`/etc/rc3.d/S09sshd`、`/etc/rc4.d/S09sshd`、`/etc/rc5.d/S09sshd`
* 你的实际需求：开发板作为 **客户端** 去 `ssh/scp` 到 PC，并不需要从外部登录开发板。

**配置步骤**

1. 停用 2/3/4/5 级别的 `sshd` 自启动：

```sh
for rl in 2 3 4 5; do
    rm -f /etc/rc${rl}.d/S*sshd
done
```

2. 保留 `/etc/init.d/sshd`，需要时可以手动启动：

   ```sh
   /etc/init.d/sshd start   # 或 service sshd start
   ```

3. 不卸载 `openssh-clients`，继续保留：

   ```sh
   ssh user@pc
   scp user@pc:/path/file /path/on/board
   ```

**结果 / 原因总结**

* 启动日志中不再出现 `Starting OpenBSD Secure Shell server: sshd` 和生成 host key 的耗时步骤。
* 系统少一个长期驻留的守护进程，资源更干净。
* 开发板仍然可以主动发起 `ssh/scp` 连接，完全满足当前使用场景。
* 真有需要时仍然可以手工开启 `sshd`，不会丢失能力，只是从“默认开启”改成“按需开启”。

---

## 2. 关闭 audit / 清理 audit.log 相关报错

**目标**

* 关闭 Linux 审计子系统和 `auditd` 服务，删掉与 `/var/log/audit/audit.log` 相关的无意义报错。
* 避免在 tmpfs 的 `/var/log` 上频繁创建/修改不需要的审计日志文件，减少启动噪音和逻辑复杂度。

**初始现象**

* 启动时反复输出：

  ```text
  chown: cannot access '/var/log/audit/audit.log': No such file or directory
  Failed to set owner -root- for -/var/log/audit/audit.log-.
  chmod: cannot access '/var/log/audit/audit.log': No such file or directory
  Failed to set mode -0600- for -/var/log/audit/audit.log-.
  ```

* `df -h` 显示根分区为 NVMe 上的 ext4，而 `/var/log` 实际为：

```sh
readlink /var/log  # -> /var/volatile/log（tmpfs）
```

  说明日志放在 tmpfs 中，每次上电 `/var/log/audit/*` 都是空的。

**需求判断**

* audit 的作用主要是安全审计 / 合规（记录谁访问了哪些关键资源）。
* 当前场景：单板/小集群，主要目标是跑容器和 HPC 应用，没有合规要求，也没有多租户/多人运维。
* 结论：**完全可以关闭审计功能**，避免无意义的开销和报错。

**技术分析**

1. 内核审计：

* 通过 `audit=0` 内核参数可以关闭内核 audit 子系统。

2. 用户空间 `auditd` 守护进程：

* 服务脚本：`/etc/init.d/auditd`
* 自启链接：`/etc/rc2.d/S20auditd` 等。

3. openEuler 的 `volatile` 脚本：

* `/etc/openeuler-volatile.cache` 中有关于 `/var/log/audit` 的规则；
* 启动时会根据这些规则去 `mkdir/chown/chmod`，在失败时输出 `"Failed to set owner ..."` 等错误；
* 这些错误来自 **volatile 初始化脚本**，和 `auditd` 本身无关。

**配置步骤**

1. **关闭内核审计**

   在 U-Boot 环境中，为启动参数增加：

   ```sh
   ... loglevel=8 audit=0
   ```

   通过 `printenv` / `setenv` 确保 `bootargs` 中包含 `audit=0`。

2. **禁用 auditd 服务**

* 去掉 runlevel 中的自启链接：

```sh
for rl in 2 3 4 5; do
      rm -f /etc/rc${rl}.d/S*auditd
done
```

* 将 `/etc/init.d/auditd` 改为“空脚本”：

  ```sh
  #!/bin/sh
  exit 0
  ```

  这样任何 `service auditd start` 都会立刻返回，不会真正启动守护进程。

3. **删除 volatile 中对 /var/log/audit 的处理**

   在 `/etc/openeuler-volatile.cache` 中找到所有关于 `/var/log/audit` 和 `/var/log/audit/audit.log` 的规则与命令，整段*
   *直接删除**，避免留半截 shell 语句导致语法错误。

   同时在 `/etc/default/openeuler-volatiles/00_core` 中注释掉对应条目，防止将来重新生成 cache 时又被加回来：

   ```text
   # d root root 0750 /var/log/audit/ none
   # f root root 0600 /var/log/audit/audit.log none
   ```

**结果 / 原因总结**

* 内核不会再启用审计子系统（`audit=0`）。
* 用户态不会再启动 `auditd`，也不会在 tmpfs 上创建/修改审计日志。
* `/etc/openeuler-volatile.cache` 不再尝试访问 `/var/log/audit*`，启动日志中关于 `audit.log` 的报错彻底消失。
* 对当前“容器 + HPC”场景没有任何功能损失，但启动更快、日志更干净、系统行为更符合实际需求。
