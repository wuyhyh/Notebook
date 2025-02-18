# Git 的日常使用

---

## Git 安装与初始化

- 在 Fedora 上安装 Git

```shell
sudo dnf install git -y
```

- 在 Ubuntu 上安装 Git

```shell
sudo apt install git -y
```

- 配置用户名和邮箱

```shell
git config --global user.name "wuyhyh"
git config --global user.email wuyhyh@gmail.com
```

- 查询配置信息

```shell
git config --list
```

- 在服务器的`~/.ssh`目录下生成公钥和私钥

```shell
cd ~/.ssh;ssh-keygen
```

- 复制公钥到 github 端

Git 的使用问题可以去问大模型，LLM 最重要的是提出具体的问题。
