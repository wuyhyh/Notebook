# 飞腾嵌入式欧拉服务器2403 LTS ISO安装镜像定制

## 1. 环境准备

获取 euler 系统镜像 https://www.phytium.com.cn/developer/44/

下载 `PSSE-2203-0407.iso`，并制作启动 U 盘



安装成功之后进入系统，在grub引导弹出时，按e进入编辑引导参数界面
（账号为root,密码为openEuler#12），添加 video=efifb:off 参数。

按 ctrl+x 执行进入系统。
进入系统之后执行以下命令即可：

```text
grubby--update-kernel=ALL--args=video=efifb:off
```

commit message

```text
Import the openEuler 22.03 LTS kernel sources as our
baseline tree.

The code is extracted from:
  kernel-source-5.10.0-136.12.0.86.aarch64.rpm
and the default configuration from:
  kernel-5.10.0-136.12.0.86.aarch64.rpm
(/boot/config-5.10.0-136.12.0.86.aarch64)

This commit also adds .gitignore and .clang-format based on
the upstream Linux kernel so that we can manage this tree
with git and keep a consistent coding style.

No functional changes are intended in this commit. It serves
as the clean baseline for downstream BSP and Phytium-specific
modifications.
```