# 调试 U-Boot

## 使用纯软件方式更新 U-Boot

flash 芯片的容量是128MB

### uboot 校验方案

- 从 flash 启动 uboot 进入命令行，然后 tftp 下载 uboot_new 到内存
- 对 uboot_new 进行校验，输出编译时间和版本号、md5校验结果，
- 如果 md5 校验结果与 PC 上一致，使用 flashw 写入 uboot_new 到 flash

### uboot 调试方案

- 从 flash 启动 uboot 进入命令行，然后 tftp 下载 uboot_new 到内存
- 加载新版的 uboot 而不是内核，如果新版的 uboot 启动成功，应该能进入新 uboot 的命令行


```text
ssh-keygen
ssh-copy-id -p 2222 git@172.16.21.119

git clone ssh://git@172.16.21.119:2222/srv/git/ft-d2000_u-boot-v1.37.git
```

