# LFS 源码包下载与校验与环境配置

> 目标：将 **Linux From Scratch 12.3** 所需的所有源码包与补丁，下载到 `$LFS/sources`，并完成 `md5sum` 校验，确认无缺漏。

---

## 1. 准备基础目录

```bash
sudo mkdir -pv $LFS/{sources,tools}
sudo chmod -v a+wt $LFS/sources
```

> sticky + 可写，便于后续下载, sticky 位保证只有文件所有者才能删除自己放进去的文件。

- 按 LFS 习惯在根目录放一个 /tools 链接

 ```bash
if [ ! -e /tools ]; then sudo ln -sv $LFS/tools /; fi
```

---

## 2. 使用中科大镜像源

### 2.1 下载列表/校验文件

先手动下载 wget-list-systemd 和 md5sums

<a href="../_static/files/wget-list-systemd" download="wget-list-systemd" class="btn btn-primary">下载 wget-list-systemd</a>
<a href="../_static/files/md5sums" download="md5sums" class="btn btn-primary">下载 md5sums</a>


### 2.2 把每行 URL 替换为 “USTC 基址 + 文件名”

```text
sed -E 's|.*/([^/]+)$|https://mirrors.ustc.edu.cn/lfs/lfs-packages/12.3/\1|' wget-list-systemd > wget-list-ustc
```

### 2.3 下载（可断点续传）

```text
wget --input-file=wget-list-ustc --continue --directory-prefix="$LFS/sources"
```

### 2.4 校验

```text
cp md5sums "$LFS/sources/"
pushd "$LFS/sources"; md5sum -c md5sums; popd
```

## 3. 快速判断是否“有缺/有损坏”

### 3.1 列出缺失或校验失败的文件

```bash
cd "$LFS/sources"
md5sum -c md5sums 2>&1 | grep -E 'FAILED|No such file' || echo "All OK"
```

### 3.2 统计应有/已下载数量（以 md5sums 为准）

```bash
req=$(awk '{print $2}' md5sums | wc -l)
have=$(ls -1 | grep -Ff <(awk '{print $2}' md5sums) | wc -l)
echo "Expect: $req  |  Have: $have"
```

> `md5sum -c` 输出全部 `OK` 即代表**既完整又正确**。出现 `FAILED` 代表内容损坏；`No such file` 代表缺包。

---

## 4. 补充说明

* **`pushd` / `popd`**：bash 的目录栈命令，用于进入/返回目录，便于脚本化处理。
* **为何要 `.patch`**：补丁用于修正源码的 bug/兼容性问题；在相应软件包章节会明确提示何时执行：

  ```bash
  patch -Np1 -i ../<package>-<version>-<desc>.patch
  ```
* **断点续传**：`wget -c` 可以反复执行，已下载文件会跳过未再下载；损坏文件会在校验时暴露，重新下载即可。
* **磁盘空间**：源码+构建缓存建议预留 ≥30–60 GB，更舒适的范围是 80–100 GB。

## 5. 第一次编译前的环境配置

### 5.1 创建有限目录布局

以 root 身份，执行以下命令创建所需的目录布局：

```text
mkdir -pv $LFS/{etc,var} $LFS/usr/{bin,lib,sbin}

for i in bin lib sbin; do
ln -sv usr/$i $LFS/$i
done

case $(uname -m) in
x86_64) mkdir -pv $LFS/lib64 ;;
esac
```

### 5.2 添加 LFS 用户

为了创建新用户，以 root 身份执行以下命令：

```text
groupadd lfs
useradd -s /bin/bash -g lfs -m -k /dev/null lfs
```

### 5.3 $LFS 中所有目录的所有者

将 lfs 设为 $LFS 中所有目录的所有者，使 lfs 对它们拥有完全访问权：

```text
chown -v lfs $LFS/{usr{,/*},var,etc,tools}
case $(uname -m) in
x86_64) chown -v lfs $LFS/lib64 ;;
esac
```

### 5.4 配置 bash

为了保证 lfs 用户环境的纯净，检查 /etc/bash.bashrc 是否存在，如果它存在就将它移走

- 以 root 用户身份，运行：

```text
[ ! -e /etc/bash.bashrc ] || mv -v /etc/bash.bashrc /etc/bash.bashrc.NOUSE
```

- 使用下面的命令切换用户：

```text
su - lfs
```

为了配置一个良好的工作环境，我们为 bash 创建两个新的启动脚本。

- 以 lfs 的身份，执行以下命令，创建一个新的 .bash_profile：

```text
cat > ~/.bash_profile << "EOF"
exec env -i HOME=$HOME TERM=$TERM PS1='\u:\w\$ ' /bin/bash
EOF
```

- 现在我们创建一个 .bashrc 文件：

```text
cat > ~/.bashrc << "EOF"
set +h
umask 022
LFS=/mnt/lfs
LC_ALL=POSIX
LFS_TGT=$(uname -m)-lfs-linux-gnu
PATH=/usr/bin
if [ ! -L /bin ]; then PATH=/bin:$PATH; fi
PATH=$LFS/tools/bin:$PATH
CONFIG_SITE=$LFS/usr/share/config.site
export LFS LC_ALL LFS_TGT PATH CONFIG_SITE
EOF
```

- 为了并行编译加快速度，将 MAKEFLAGS 的设置写入 .bashrc 中：

```text
cat >> ~/.bashrc << "EOF"
export MAKEFLAGS=-j$(nproc)
EOF
```

- 强制 bash shell 读取刚才创建的配置文件：

```text
source ~/.bash_profile
```
