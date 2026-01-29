# 内核 RPM 打包流程

下面把“交叉编译内核 → 打 RPM → 带上 kernel-devel → 拷到商用开发板安装切换”的完整流程重新整理一遍，并把你说的“后缀不用
cust1，改成基线版本”的处理方式讲清楚。

先把关键事实说死：

* **只要你要让新内核和发行版内核共存并可回滚，就必须有某种区分**。区分可以是 `LOCALVERSION`（出现在 `uname -r` 和
  `/lib/modules/<kver>` 里），也可以只改 RPM 的 Release。
* 你说的“改成基线版本”，我理解为：`uname -r` 仍然看起来像发行版基线（比如 `5.10.0-216` 这一类），不要出现 `-cust1`
  。这可以做到，但代价是：**你会覆盖/替换同版本的模块目录和 /boot 文件，回滚难度变大**，而且 dnf/rpm 可能认为“版本没变”而不升级。

我给你两种模式：你选“安全模式”当主线，“基线模式”只在你明确接受覆盖风险时用。

---

## 0. 两种命名模式（你必须先选一个）

### A) 安全模式（推荐）

* 内核 release 带一个很轻的后缀，比如 `-baseline1`、`-phy1`、`-wuyuhang1`，用于区分模块目录。
* 好处：可并存、可回滚、最稳。
* 坏处：`uname -r` 不再完全等同发行版基线。

### B) 基线模式（你想要的）

* 不加任何 `LOCALVERSION`，让 `uname -r` 尽量等同基线。
* 你必须同时保证 **RPM 的 Version-Release 比原来的新**，否则板子上不会升级。
* 风险：可能覆盖发行版同名模块目录和引导文件；回滚要靠事先备份或手工 grub 选旧项。

下面流程两种模式都能用，我会在关键点标注差异。

---

## 1) 构建机准备（x86_64 openEuler）

### 1.1 安装依赖

```bash
sudo dnf install -y \
  gcc make bc flex bison elfutils-libelf-devel openssl-devel ncurses-devel dwarves \
  git rsync perl python3 \
  rpm-build rpmdevtools
rpmdev-setuptree
```

### 1.2 准备交叉工具链与环境变量

你之前已经有 `env-aarch64.sh` 这种只包含 export 的脚本，这是正确做法，避免 PATH 污染 host 工具（尤其是 `as`）。
确保你的环境里至少有：

* `ARCH=arm64`
* `CROSS_COMPILE=aarch64-linux-gnu-`（或你实际工具链前缀）
* host 工具不被替换（`/usr/bin/as` 等仍是 x86_64 版本）

---

## 2) 交叉编译内核（可重复执行）

假设内核源码在：
`~/src/openeuler-5.10.0-xxx-src-master/`

### 2.1 配置与版本策略

进入源码：

```bash
source ~/env-aarch64.sh
cd ~/src/openeuler-5.10.0-136-src-master
```

#### 安全模式（推荐）

```bash
export LOCALVERSION=-baseline1
```

#### 基线模式（你要求的）

```bash
unset LOCALVERSION
# 并确保 .config 里 CONFIG_LOCALVERSION 为空
# （如果你之前写过，记得清掉）
```

### 2.2 配置

```bash
make O=build ARCH=arm64 olddefconfig
```

### 2.3 编译

```bash
make O=build ARCH=arm64 -j"$(nproc)" Image modules dtbs
```

### 2.4 确认 kernelrelease（非常关键）

```bash
make -s O=build ARCH=arm64 kernelrelease
```

记下输出，这个值将决定：

* `/lib/modules/<kver>/`
* `kernel-devel` 的目录名 `/usr/src/kernels/<kver>/`

---

## 3) 生成内核 RPM（kernel + modules + headers）

你已经验证过 `binrpm-pkg` 生成的 `kernel` RPM 里包含 `/lib/modules/<kver>`，这是对的。

```bash
make O=build ARCH=arm64 -j"$(nproc)" binrpm-pkg
```

产物默认在：

```bash
ls -lh ~/rpmbuild/RPMS/aarch64/
```

你应当至少看到：

* `kernel-*.aarch64.rpm`
* `kernel-headers-*.aarch64.rpm`

### 3.1 验证 kernel 包含模块

```bash
rpm -qpl ~/rpmbuild/RPMS/aarch64/kernel-*.rpm | grep '^/lib/modules/' | head
```

---

## 4) 生成 kernel-devel RPM（给别人上板子编外部模块用）

你前面踩的坑：`BuildArch: aarch64` 在 x86_64 主机上会被 rpmbuild 拒绝。正确做法：**kernel-devel 打成 noarch，并用 Requires
锁定内核版本**。

### 4.1 生成 staging 目录

```bash
KREL=$(make -s O=build ARCH=arm64 kernelrelease)     # 例如 5.10.0-baseline1 或 5.10.0-216...
VER=${KREL/-/_}                                      # RPM Version 里不能用 '-'，转成 '_'

STAGE=~/kdevel_stage/usr/src/kernels/$KREL
rm -rf ~/kdevel_stage
mkdir -p "$STAGE"

# 准备外部模块编译所需文件（尽量保留 Makefile/Kconfig/scripts/include）
rsync -a --delete \
  --exclude '.git' \
  --exclude 'build' \
  --exclude '*.o' --exclude '*.cmd' \
  ./ "$STAGE/"

cp -f build/.config "$STAGE/.config"
make O=build ARCH=arm64 prepare modules_prepare
cp -f build/Module.symvers "$STAGE/" 2>/dev/null || true

rsync -a build/include/generated/ "$STAGE/include/generated/"
rsync -a build/arch/arm64/include/generated/ "$STAGE/arch/arm64/include/generated/"
```

### 4.2 打 tar + spec + rpmbuild（noarch）

先从你已有的 kernel rpm 解析 `REL`（release 数字）。最简单：

```bash
KERNEL_RPM=$(ls -1 ~/rpmbuild/RPMS/aarch64/kernel-*.rpm | head -n1)
REL=$(rpm -qp --qf '%{RELEASE}\n' "$KERNEL_RPM")
echo "REL=$REL"
```

打 tar：

```bash
tar -C ~/kdevel_stage -czf ~/rpmbuild/SOURCES/kernel-devel-${VER}.tar.gz .
```

写 spec：

```bash
SPEC=~/rpmbuild/SPECS/kernel-devel.spec
cat > "$SPEC" <<EOF
Name:           kernel-devel
Version:        ${VER}
Release:        ${REL}%{?dist}
Summary:        Kernel development package for building external modules
License:        GPLv2
BuildArch:      noarch
Source0:        kernel-devel-${VER}.tar.gz

# 锁定到同版本 kernel，避免误装
Requires:       kernel = ${VER}-${REL}

%define krel ${KREL}

%description
Kernel build tree to build external modules against the installed kernel.

%prep
%setup -q -c -T
tar -xzf %{SOURCE0}

%install
mkdir -p %{buildroot}/
cp -a usr %{buildroot}/

%files
/usr/src/kernels/%{krel}

%changelog
* Sat Jan 03 2026 wuyuhang - ${VER}-${REL}
- Build kernel-devel package for external module builds
EOF
```

构建：

```bash
rpmbuild -bb "$SPEC"
ls -lh ~/rpmbuild/RPMS/noarch/kernel-devel-*.rpm
```

---

## 5) 拷贝到商用开发板并安装

要拷的 3 个包：

* `~/rpmbuild/RPMS/aarch64/kernel-*.rpm`
* `~/rpmbuild/RPMS/aarch64/kernel-headers-*.rpm`
* `~/rpmbuild/RPMS/noarch/kernel-devel-*.rpm`

拷贝：

```bash
scp ~/rpmbuild/RPMS/aarch64/kernel-*.rpm \
    ~/rpmbuild/RPMS/aarch64/kernel-headers-*.rpm \
    ~/rpmbuild/RPMS/noarch/kernel-devel-*.rpm \
    root@<board_ip>:/root/kernel_rpms/
```

板子上安装：

```bash
cd /root/kernel_rpms
sudo dnf install -y ./*.rpm
```

安装后检查：

```bash
ls -l /lib/modules | tail
ls -l /usr/src/kernels | tail
```

---

## 6) 切换启动并验证

安装后先确认 /boot 有新内核文件：

```bash
ls -lh /boot | grep -E 'vmlinuz|initramfs|System.map|config' | tail -n 50
```

重启后：

```bash
uname -r
```

---

# 关于“后缀改成基线版本”的建议（我直说）

如果你的目标是“商用板就是发行版基线名，看起来干净”，可以用基线模式，但我不建议你长期这样做，因为它会把回滚和排错变难。

更合理的折中是：

* `uname -r` 仍然是基线 + 一个很轻的后缀（比如 `-baseline1`），这样大家一眼知道这是你们内部内核，同时不影响模块目录隔离、不会覆盖发行版的
  `/lib/modules/<kver>/`。
* RPM 的 Version/Release 继续严格递增，保证 dnf 行为确定。

如果你坚持“完全不要后缀”，那你至少要做到：

1. 确保 `make kernelrelease` 输出严格等于你要替换的那个基线（包括 `EXTRAVERSION`/localversion 都为空）
2. RPM 的 `Release` 必须比发行版更大，且你得接受覆盖模块目录的后果
3. 安装前备份 `/boot` 和 `/lib/modules/<kver>`（否则出问题回滚成本很高）

---

你下一步最关键的是：你希望“基线版本”具体长什么样？
是像 openEuler 官方那种 `5.10.0-216.0.0.XXX.aarch64`，还是你现在 `5.10.0` 这种？你把
`make -s O=build ARCH=arm64 kernelrelease` 的输出贴一下，我就能告诉你应该采用哪种命名策略才能既“看起来像基线”，又不把自己坑死。

基本可以了。你现在已经得到一套“能在 aarch64 板子上换内核 + 能在板子上编外部驱动”的三件套：

* `aarch64/kernel-5.10.0_baseline1-2.aarch64.rpm`
* `aarch64/kernel-headers-5.10.0_baseline1-2.aarch64.rpm`
* `noarch/kernel-devel-5.10.0_baseline1-2.noarch.rpm`

这就是你要的结果。

但我建议你再做两步“最后确认”，避免明天上板子翻车。

---

## 1) 确认 kernel-devel 真的绑定到对应 kernel 版本

你在 rpmbuild 输出里看到它 `Provides: kernel-devel = 5.10.0_baseline1-2`，这没问题；关键是 **Requires** 是否锁死到你这版
kernel。

在构建机上执行：

```bash
rpm -qpR ~/rpmbuild/RPMS/noarch/kernel-devel-5.10.0_baseline1-2.noarch.rpm | grep -E '^kernel( |=)'
```

你希望看到类似：

* `kernel = 5.10.0_baseline1-2`

如果没有，说明你的 spec 里没加锁版本。没锁版本也能用，但容易被别人装到错误内核上，后面编驱动对不上就开始扯皮。我建议锁上。

---

## 2) 确认 kernel RPM 里确实包含模块目录

你之前已经验证过一次 cust1，这次 baseline1 也再确认一次：

```bash
rpm -qpl ~/rpmbuild/RPMS/aarch64/kernel-5.10.0_baseline1-2.aarch64.rpm | grep '^/lib/modules/' | head
```

能看到 `/lib/modules/5.10.0-baseline1/...` 之类就稳了。

---

## 明天上板子怎么装（最稳）

把三包都拷过去：

```bash
scp ~/rpmbuild/RPMS/aarch64/kernel-5.10.0_baseline1-2.aarch64.rpm \
    ~/rpmbuild/RPMS/aarch64/kernel-headers-5.10.0_baseline1-2.aarch64.rpm \
    ~/rpmbuild/RPMS/noarch/kernel-devel-5.10.0_baseline1-2.noarch.rpm \
    root@<board_ip>:/root/kernel_rpms/
```

板子上：

```bash
cd /root/kernel_rpms
sudo dnf install -y ./*.rpm
ls -l /lib/modules | grep baseline1
ls -l /usr/src/kernels | grep baseline1
```

然后重启进入新内核：

```bash
reboot
# 起后
uname -r
```

---

## 你现在这个“baseline1”命名是合理的

你说不要 cust1，而要“基线版本”。`baseline1` 这种后缀我认为比 cust1 更像你要表达的意思：这是基线分支的第 1
个内部构建，同时仍然保留了模块目录隔离和可回滚能力。

如果你下一步想更“发行版风格”，可以把后缀改成类似：

* `-oe2203sp4.1` 或 `-oe2203sp4.0`（更贴近 openEuler 语境）
* 或者按你们团队规范：`-base.r1`

但不建议完全去掉后缀。

---

结论：你现在这套包已经可以用了；按上面两条检查再确认一下依赖锁定和模块目录，就可以直接交付上板子安装。



从“内核已经编译成功（Image/modules/dtbs 都有了）”开始，下面把 **打出能直接给别人用的 RPM 三件套（kernel / kernel-headers / kernel-devel）** 的流程重新梳理一遍，并且把你刚刚踩到的坑（BTF、tools 被裁掉、板子上还得 prepare）一次性解决掉。

目标：别人把 3 个 RPM 拷到板子上 `dnf install` 后，**不需要再跑 `make prepare`**，直接能在板子上编外部模块。

---

# 0. 约定与目录

假设你在构建机（x86_64 openEuler VM）里：

* 内核源码：`~/src/openeuler-5.10.0-136-src-master`
* 输出目录：`O=build`
* 交叉编译环境已 `source env-aarch64.sh`
* 你的内核 release（`make kernelrelease`）类似：`5.10.0-baseline1`

下面所有命令都在源码根目录执行。

---

# 1) 结束编译阶段：确保 build 目录“干净且可复现”

你已经编译完了，但要打“可用的 kernel-devel”，必须确保 **prepare/modules_prepare** 和 **符号文件**都齐。

```bash
source ~/env-aarch64.sh
cd ~/src/openeuler-5.10.0-136-src-master

# 1) 确保 .config 完整
make O=build ARCH=arm64 olddefconfig

# 2) 编译内核镜像/模块/DTB（你已经做过可以略）
make O=build ARCH=arm64 -j"$(nproc)" Image modules dtbs

# 3) 关键：生成外部模块编译所需的 generated 文件、脚本和符号
make O=build ARCH=arm64 prepare modules_prepare

# 4) 记录内核 release（后面路径会用到）
KREL=$(make -s O=build ARCH=arm64 kernelrelease)
echo "KREL=$KREL"
```

说明：这一步在构建机做完后，你再打包 kernel-devel，板子上就不应该再遇到 `autoconf.h/auto.conf` 缺失，也不会卡 BTF。

---

# 2) 生成 kernel 与 kernel-headers RPM（aarch64）

这部分你已经跑通了，直接固定流程：

```bash
make O=build ARCH=arm64 -j"$(nproc)" binrpm-pkg
```

产物检查：

```bash
ls -lh ~/rpmbuild/RPMS/aarch64/kernel-*.rpm
ls -lh ~/rpmbuild/RPMS/aarch64/kernel-headers-*.rpm
```

确认 kernel RPM 包含模块：

```bash
rpm -qpl ~/rpmbuild/RPMS/aarch64/kernel-*.rpm | grep '^/lib/modules/' | head
```

---

# 3) 重新制作“可直接用”的 kernel-devel RPM（noarch）

你之前的问题来自两个点：

1. 你把 `tools/` 排除了，导致 prepare 时缺 `tools/build/Makefile.include`，触发 BTF resolve 流程失败
2. kernel-devel 树里缺少 generated 文件/auto.conf 等（或者没提前 prepare）

所以：**新的 kernel-devel 要满足这三个条件**

* 包含 `tools/`（至少包含 `tools/build/Makefile.include` 以及 BPF 相关路径）
* 包含 `build` 生成的关键文件：`include/generated/autoconf.h`、`include/config/auto.conf`、generated headers、`Module.symvers` 等
* 不要求在板子上再跑 `make prepare modules_prepare`

## 3.1 从已生成的 kernel RPM 里取 Version/Release

这样能保证 devel 与 kernel 完全对齐。

```bash
KERNEL_RPM=$(ls -1 ~/rpmbuild/RPMS/aarch64/kernel-*.rpm | head -n1)
VER=$(rpm -qp --qf '%{VERSION}\n' "$KERNEL_RPM")
REL=$(rpm -qp --qf '%{RELEASE}\n' "$KERNEL_RPM")
echo "VER=$VER REL=$REL"
```

同时拿 kernelrelease（目录名用）：

```bash
KREL=$(make -s O=build ARCH=arm64 kernelrelease)
echo "KREL=$KREL"
```

注意：`VER` 往往是 `5.10.0_baseline1` 这种（RPM 里用 `_`），而 `KREL` 往往是 `5.10.0-baseline1`（uname -r 用 `-`）。这是正常的，你 devel 包里目录必须按 **KREL** 来。

## 3.2 准备 staging：用源码树 + build 的关键生成物补齐

```bash
STAGE=~/kdevel_stage/usr/src/kernels/$KREL
rm -rf ~/kdevel_stage
mkdir -p "$STAGE"

# 复制源码树：这次不要排除 tools/
rsync -a --delete \
  --exclude '.git' \
  --exclude 'build' \
  --exclude '*.o' --exclude '*.cmd' --exclude '*.tmp' \
  --exclude '.*.cmd' \
  ./ "$STAGE/"

# 放入 build 产出的配置与关键文件
cp -f build/.config "$STAGE/.config"
cp -f build/Module.symvers "$STAGE/" 2>/dev/null || true
cp -f build/System.map "$STAGE/" 2>/dev/null || true
cp -f build/vmlinux "$STAGE/" 2>/dev/null || true

# 关键：把 prepare/modules_prepare 生成的内容同步进去
# 这些就是你之前缺的
rsync -a build/include/generated/ "$STAGE/include/generated/"
rsync -a build/include/config/ "$STAGE/include/config/"
rsync -a build/arch/arm64/include/generated/ "$STAGE/arch/arm64/include/generated/"

# 补充：外部模块构建常用的 scripts 输出
rsync -a build/scripts/ "$STAGE/scripts/"

# 保险：确认 tools/build/Makefile.include 存在
test -f "$STAGE/tools/build/Makefile.include"
```

如果最后一行 `test` 失败，说明你的源码树本身缺 `tools/build/Makefile.include`（不太可能），或 rsync 没拷进去（路径错误）。

## 3.3 打 tar

```bash
rpmdev-setuptree
tar -C ~/kdevel_stage -czf ~/rpmbuild/SOURCES/kernel-devel-${VER}.tar.gz .
```

## 3.4 写 spec（noarch + 强绑定 kernel 版本）

```bash
SPEC=~/rpmbuild/SPECS/kernel-devel.spec
cat > "$SPEC" <<EOF
Name:           kernel-devel
Version:        ${VER}
Release:        ${REL}%{?dist}
Summary:        Kernel build tree for external module builds
License:        GPLv2
BuildArch:      noarch
Source0:        kernel-devel-${VER}.tar.gz

# 强绑定，防止装到别的内核上
Requires:       kernel = ${VER}-${REL}

%define krel ${KREL}

%description
This package contains the kernel build tree sufficient to build external
kernel modules against the installed kernel.

%prep
%setup -q -c -T
tar -xzf %{SOURCE0}

%install
mkdir -p %{buildroot}/
cp -a usr %{buildroot}/

%files
/usr/src/kernels/%{krel}

%changelog
* Sat Jan 03 2026 wuyuhang - ${VER}-${REL}
- Build kernel-devel package for external module builds
EOF
```

## 3.5 构建 kernel-devel RPM

```bash
rpmbuild -bb "$SPEC"
ls -lh ~/rpmbuild/RPMS/noarch/kernel-devel-*.rpm
```

---

# 4) 交付前在构建机做“可用性自检”（强烈建议）

你要保证：板子上装完 **不需要 make prepare**。

最简单的自检：在构建机把 tar 解开看看关键文件是否存在（你之前缺的就是这些）：

```bash
tmp=/tmp/kdevel_check
rm -rf $tmp && mkdir -p $tmp
tar -xf ~/rpmbuild/SOURCES/kernel-devel-${VER}.tar.gz -C $tmp

ls -l $tmp/usr/src/kernels/$KREL/include/config/auto.conf
ls -l $tmp/usr/src/kernels/$KREL/include/generated/autoconf.h
ls -l $tmp/usr/src/kernels/$KREL/tools/build/Makefile.include
```

这三条都存在，基本就不会再在板子上炸。

---

# 5) 板子侧的标准安装与验证

拷贝三件套：

* `~/rpmbuild/RPMS/aarch64/kernel-*.rpm`
* `~/rpmbuild/RPMS/aarch64/kernel-headers-*.rpm`
* `~/rpmbuild/RPMS/noarch/kernel-devel-*.rpm`

板子上安装：

```bash
sudo dnf install -y ./*.rpm
```

验证“无需 prepare 直接编模块”：

```bash
ls -l /usr/src/kernels/$(uname -r)/include/config/auto.conf
ls -l /usr/src/kernels/$(uname -r)/tools/build/Makefile.include

cd ~/kmod_hello
make
```

---

# 6) 你这套流程后面给团队用的规则（建议）

* 交付内核升级包：**永远三件套一起发**：kernel + kernel-headers + kernel-devel
* 外部模块编译统一写 Makefile：
  `KDIR ?= /usr/src/kernels/$(uname -r)`
* 不允许拿别的 `uname -r` 编出来的 `.ko` 直接 insmod（你已经验证过会 Unknown symbol）

---

如果你愿意，我可以把上面流程整理成你项目里的一个 `build_kernel_rpms.sh` 脚本（带检查点、失败直接退出、产物路径固定），你以后每次改内核只要跑一条命令就能得到三件套。你告诉我你源码路径和工具链脚本固定位置，我就按你的目录结构写死进去。

