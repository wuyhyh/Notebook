# 使用QEMU运行Linux内核

## 准备工作

PC: x86_64 intel 13700k 24核 64G 1TB
fedora 41 server

```
root@fedora41-amd64:~# qemu-system-aarch64 --version
QEMU emulator version 9.1.3 (qemu-9.1.3-1.fc41)
Copyright (c) 2003-2024 Fabrice Bellard and the QEMU Project developers
root@fedora41-amd64:~# arch
x86_64
root@fedora41-amd64:~# aarch64-linux-gnu-gcc --version
aarch64-linux-gnu-gcc (GCC) 14.2.1 20240912 (Red Hat Cross 14.2.1-2)
Copyright (C) 2024 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

下载5.0内核代码

```shell
git clone git@github.com:runninglinuxkernel/runninglinuxkernel_5.0.git
```
编译内核并创建文件系统
```shell
cd runninglinuxkernel_5.0
./run_rlk_arm64.sh build_kernel
```

```shell
cd runninglinuxkernel_5.0
sudo ./run_rlk_arm64.sh build_rootfs
```

运行编译好的ARM64版本的Linux系统
```shell
./run_rlk_arm64.sh run
```

