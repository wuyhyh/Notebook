# 01-用户权限与sudo基础

## 1 文档目标

本文用于帮助实习生理解 Linux 中的用户、权限和 `sudo` 基础用法，能够完成常见的权限查看、文件权限修改、管理员命令执行等操作。

学习完本文后，应能完成以下任务：

1. 查看当前用户身份
2. 理解普通用户和 root 用户的区别
3. 查看文件权限
4. 修改文件权限和所有者
5. 使用 `sudo` 执行管理员命令
6. 避免常见的权限误操作

## 2 Linux 用户基础

## 2.1 当前用户是谁

查看当前登录用户：

```bash
whoami
```

查看当前用户的 UID、GID 和所属用户组：

```bash
id
```

示例输出：

```text
uid=1000(test) gid=1000(test) groups=1000(test),10(wheel)
```

其中：

| 字段 | 含义 |
|---|---|
| `uid` | 用户 ID |
| `gid` | 主用户组 ID |
| `groups` | 当前用户所属的所有用户组 |

## 2.2 root 用户是什么

`root` 是 Linux 中权限最高的管理员用户，UID 固定为 `0`。

root 用户可以：

1. 修改系统配置文件
2. 安装和删除软件包
3. 创建和删除用户
4. 修改任意文件的权限和所有者
5. 启动、停止系统服务

普通用户不应该长期使用 root 身份工作，否则误操作的风险很高。

## 3 文件权限基础

## 3.1 查看文件权限

使用 `ls -l` 查看文件权限：

```bash
ls -l
```

示例：

```text
-rw-r--r-- 1 user user 1024 Apr 29 10:00 test.txt
```

其中第一列表示权限：

```text
-rw-r--r--
```

可以拆成四部分：

| 部分 | 含义 |
|---|---|
| `-` | 文件类型 |
| `rw-` | 文件所有者权限 |
| `r--` | 同组用户权限 |
| `r--` | 其他用户权限 |

## 3.2 r、w、x 的含义

| 权限 | 对文件的含义 | 对目录的含义 |
|---|---|---|
| `r` | 读取文件内容 | 查看目录内容 |
| `w` | 修改文件内容 | 创建、删除、重命名目录内文件 |
| `x` | 执行文件 | 进入目录 |

注意：目录如果没有 `x` 权限，即使有 `r` 权限，也无法正常进入该目录。

## 4 chmod 修改权限

## 4.1 使用数字方式修改权限

常见数字含义：

| 数字 | 权限 |
|---|---|
| `4` | 读 |
| `2` | 写 |
| `1` | 执行 |

组合示例：

| 数字 | 权限 |
|---|---|
| `7` | `rwx` |
| `6` | `rw-` |
| `5` | `r-x` |
| `4` | `r--` |

示例：

```bash
chmod 644 test.txt
```

表示：

```text
所有者：可读可写
同组用户：只读
其他用户：只读
```

常见权限：

| 命令 | 作用 |
|---|---|
| `chmod 644 file` | 普通文本文件常用权限 |
| `chmod 755 script.sh` | 脚本或可执行文件常用权限 |
| `chmod 600 id_rsa` | 私钥文件常用权限 |

## 4.2 给脚本添加执行权限

```bash
chmod +x test.sh
```

然后执行：

```bash
./test.sh
```

## 5 chown 修改所有者

## 5.1 修改文件所有者

```bash
sudo chown user file.txt
```

表示将 `file.txt` 的所有者修改为 `user`。

## 5.2 修改所有者和用户组

```bash
sudo chown user:group file.txt
```

示例：

```bash
sudo chown root:root config.txt
```

## 5.3 递归修改目录

```bash
sudo chown -R user:group directory/
```

注意：`-R` 会递归修改目录下所有文件，执行前必须确认路径正确。

## 6 sudo 基础

## 6.1 sudo 是什么

`sudo` 用于让普通用户临时以管理员权限执行命令。

示例：

```bash
sudo vim /etc/hosts
```

表示用管理员权限编辑 `/etc/hosts`。

## 6.2 常见 sudo 用法

| 命令 | 作用 |
|---|---|
| `sudo command` | 以管理员权限执行命令 |
| `sudo -i` | 进入 root 登录环境 |
| `sudo su` | 切换到 root 用户 |
| `sudo !!` | 用 sudo 重新执行上一条命令 |

示例：

```bash
dnf install vim
```

如果提示权限不足，可以使用：

```bash
sudo dnf install vim
```

## 6.3 判断用户是否有 sudo 权限

执行：

```bash
sudo -v
```

如果用户有 sudo 权限，会要求输入当前用户密码。

如果没有权限，可能提示：

```text
user is not in the sudoers file
```

在 openEuler、CentOS、Fedora 等系统中，常见管理员用户组是 `wheel`。

查看当前用户是否在 `wheel` 组：

```bash
id
```

## 7 修改系统配置文件的权限习惯

## 7.1 推荐方式

修改系统配置文件时，推荐直接使用：

```bash
sudo vim /etc/hosts
```

不要先切换到 root 再进行大量操作。

## 7.2 修改前先备份

```bash
sudo cp /etc/hosts /etc/hosts.bak
```

修改出错时恢复：

```bash
sudo cp /etc/hosts.bak /etc/hosts
```

## 7.3 避免滥用 chmod 777

不要随便执行：

```bash
chmod 777 file
```

`777` 表示所有用户都可以读、写、执行，权限过大，容易带来安全风险。

如果只是想让脚本能执行，应该使用：

```bash
chmod +x script.sh
```

## 8 常见问题

## 8.1 Permission denied 是什么原因

`Permission denied` 表示权限不足。

常见原因：

1. 当前用户没有读权限
2. 当前用户没有写权限
3. 当前用户没有目录进入权限
4. 执行脚本时没有 `x` 权限
5. 修改系统文件时没有使用 `sudo`

## 8.2 为什么不能直接修改 /etc 下的文件

`/etc` 目录下通常是系统配置文件，普通用户没有写权限。

例如：

```bash
vim /etc/hosts
```

可能无法保存。

应该使用：

```bash
sudo vim /etc/hosts
```

## 8.3 sudo 和 root 有什么区别

| 项目 | sudo | root |
|---|---|---|
| 使用方式 | 临时提权 | 长期管理员身份 |
| 安全性 | 较高 | 风险较高 |
| 推荐程度 | 推荐 | 不建议长期使用 |

日常开发中，优先使用 `sudo`，不要长期停留在 root shell 中。

## 9 必须掌握的命令总结

| 命令 | 作用 |
|---|---|
| `whoami` | 查看当前用户 |
| `id` | 查看 UID、GID 和用户组 |
| `ls -l` | 查看文件权限 |
| `chmod 644 file` | 设置普通文件权限 |
| `chmod +x script.sh` | 添加执行权限 |
| `chown user file` | 修改文件所有者 |
| `sudo command` | 以管理员权限执行命令 |
| `sudo vim file` | 用管理员权限编辑文件 |
| `sudo -v` | 检查 sudo 权限 |

## 10 练习任务

## 10.1 查看当前用户信息

```bash
whoami
id
```

记录当前用户名称、UID、GID 和所属用户组。

## 10.2 创建测试文件并查看权限

```bash
touch permission-test.txt
ls -l permission-test.txt
```

观察文件的默认权限。

## 10.3 修改文件权限

```bash
chmod 644 permission-test.txt
ls -l permission-test.txt
```

确认权限变化。

## 10.4 创建脚本并添加执行权限

```bash
vim hello.sh
```

写入：

```bash
#!/bin/bash
echo "hello sudo"
```

添加执行权限：

```bash
chmod +x hello.sh
```

执行：

```bash
./hello.sh
```

## 11 小结

Linux 权限学习的重点是理解三个问题：

```text
谁在操作？
操作哪个文件？
有没有对应权限？
```

日常工作中需要养成以下习惯：

1. 先用 `ls -l` 查看权限
2. 修改系统文件前先备份
3. 需要管理员权限时使用 `sudo`
4. 不要随便使用 `chmod 777`
5. 使用 `-R` 递归操作前必须确认路径
