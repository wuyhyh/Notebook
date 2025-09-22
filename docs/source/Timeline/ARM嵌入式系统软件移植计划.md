# ARM 嵌入式系统软件移植计划

## 1. 开发环境搭建

### 1.1 使用 Git 进行版本管理，支持分布式协作开发

> Linux 服务器仓库
> ```text
> git clone ssh://git@172.16.21.220:2222/srv/git/ft-d2000_u-boot-v1.37.git
> ```
> ```text
> git clone ssh://git@172.16.21.220:2222/srv/git/image_fix_d2000_v1.71.git
> ```

### 1.2 建立分布式文档管理仓库，支持 md 文档离线浏览器阅读

> 本地仓库和 Linux 服务器仓库
> ```text
> git clone  C:/Users/wuyuhang/git-backups/HPC_project.git
> ```
> ```text
> git clone ssh://git@172.16.21.220:2222/srv/git/HPC_project.git
> ```

## 2. U-Boot 开发

### 2.1 打包脚本

摸清打包脚本PBF参数配置： DDR 训练、PCIe 工作模式配置问题的解决办法

### 2.2 板级配置文件

- 编译板级配置文件丢失，根据 `.config` 文件还原了板级配置
- uboot 功能需要进一步定制，需要修改版级配置文件，使用 `menuconfig`修改编译组件

### 2.3 uboot 调试

详细记录在[U-Boot调试](./U-Boot调试.md)

## 3. 使用 QEMU 模拟

在 QEMU 里保证内核配置、文件系统、用户空间、通用驱动与基础启动链是健康的，再去攻克真机的板级差异

使用 QEMU 提供的 virt 平台模拟真实硬件，先把引导链跑通

## 4. 飞腾 bsp

飞腾 bsp:

https://gitee.com/phytium_embedded/phytium-openeuler-embedded-bsp

## 5. oe-build

https://pages.openeuler.openatom.cn/embedded/docs/build/html/openEuler-22.03-LTS-SP4/yocto/index.html
