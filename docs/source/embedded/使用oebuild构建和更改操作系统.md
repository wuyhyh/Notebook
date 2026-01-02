# 使用oebuild构建和更改操作系统

## 安装必要的主机包

```sh
# 安装必要的软件包
sudo apt-get install python3 python3-pip docker docker.io
#如果安装过 oebuild 但版本不是 v0.1.0.1, 需要先卸载 oebuild, sudo pip uninstall oebuild
sudo pip install oebuild==0.1.0.1	

# 配置docker环境
sudo usermod -a -G docker $(whoami)
sudo systemctl daemon-reload && sudo systemctl restart docker
sudo chmod o+rw /var/run/docker.sock
```

## 初始化oebuild构建环境

```sh
# <work> 为要创建的工作目录
oebuild init -b openEuler-24.03-LTS <work>
	
#创建编译配置文件
cd <work>
oebuild update
```

“oebuild init”命令会初始化工作目录，“oebuild update”命令会下载目标版本的项目源码及构建容器， 完成后会在工作目录创建 src 目录 和 oebuild.log 等文件。src 目录是用来存放依赖的软件包源码的，包括 yocto-meta-openeuler、yocto-poky 等。

## 获取飞腾软件包

```sh
rm -rf src/yocto-meta-openeuler/bsp/meta-phytium

git clone https://gitee.com/phytium_embedded/phytium-bsp-openeuler-embedded.git 
src/yocto-meta-openeuler/bsp/meta-phytium

cp src/yocto-meta-openeuler/bsp/meta-phytium/phytium.yaml src/yocto-meta-openeuler/.oebuild/platform/
```

## oebuild构建

```sh
cd <work>
oebuild generate -p phytium
cd <work>/build/phytium
oebuild bitbake openeuler-image
```

## 镜像输出位置

```text
<work>/build/phytium/tmp/deploy/images/phytium:  kernel image ,rootfs ,dtb and phydisk.img
```



## 修改内核选项

```sh
cd <work>/build/phytium
oebuild bitbake
bitbake -c menuconfig linux-openeuler

#修改完后退出环境执行构建操作
exit
oebuild bitbake openeuler-image

```

## 修改设备树

```sh
cd <work>/build/phytium/tmp/work-shared/phytium/kernel-source/arch/arm64/boot/dts/phytium/
```

可以在该目录下修改或创建设备树

修改makefile

```
vi Makefile
```

添加下面的内容，如果修改已经添加过的设备树则不需要进行以下步骤

```text
dtb-$(CONFIG_ARCH_PHYTIUM) += <your dts name>.dtb
```

修改包含文件

```sh
$ vi <work>/src/yocto-meta-openeuler/bsp/meta-phytium/conf/machine/include/phy-base.inc 
```

添加下面内容

```
  KERNEL_DEVICETREE ??= " \
    phytium/pe2202-demo-ddr4.dtb \
    phytium/pe2201-demo-ddr4.dtb \
    phytium/pe2204-demo-ddr4.dtb \
    phytium/phytiumpi_firefly.dtb \
+   phytium/<your dts name>.dtb \
    "
```

生成设备树补丁

```sh
cd <work>build/phytium/tmp/work-shared/phytium/kernel-source
git add .
git commit -s -m "update dts"
git format-patch -1
```

补丁添加到构建系统

```sh
cp 0001-update-dts.patch  <work>/src/yocto-meta-openeuler/bsp/meta-phytium/recipes-kernel/linux/files/
vi <work>/src/yocto-meta-openeuler/bsp/meta-phytium/recipes-kernel/linux/linux-openeuler.bbappend
#加入以下内容   
SRC_URI:append = "\
    file://0001-openeuler-phytium-opensource-v2_1.patch \
    file://0001-update-dts.patch \ 
"
```

重新编译内核

```sh
make mrproper
oebuild bitbake openeuler-image
```

注意：Yocto工程需要通过打补丁的方式将改动加入到工程，不能改动Kernel source，否则执行构建操作时会报错dirty source，此时在内核源码目录执行。

```sh
make mrproper
```

会将之前的改动全部重置，再执行构建操作。

## 修改内核源码

与修改设备树类似，修改之后生成补丁，并添加到linux-openeuler.bbappend文件中，重新编译内核

## 相关问题

### 编译内核相关问题

编译时需要先拓展虚拟机内存

```sh
# 查看当前内存和swap
free -h

# 创建8GB swap文件
sudo dd if=/dev/zero of=/swapfile bs=1G count=8
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 确认启用
swapon --show

```

GDB 链接阶段 (link) 出错

```text
undefined reference to `_initialize_ada_language()'
undefined reference to `ada_is_tagged_type(type*, int)'
...
collect2: error: ld returned 1 exit status
```

添加gnat链接库

```sh
sudo apt update
sudo apt install gnat
```
