# macOS 环境配置

- 创建大小写敏感的磁盘镜像

```shell
hdiutil create -size 40g -type SPARSEBUNDLE -fs 'Case-sensitive APFS' -volname LinuxKernel ~/LinuxKernel.dmg
```

- 挂载镜像

```shell
hdiutil attach ~/LinuxKernel.dmg
```

- 启动 lima 虚拟机

```shell
limactl stop default
limactl start default
```
