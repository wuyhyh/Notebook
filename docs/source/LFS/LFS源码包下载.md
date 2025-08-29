# LFS 第三章：源码包下载与校验（USTC 镜像）

> 目标：将 **Linux From Scratch 12.3** 所需的所有源码包与补丁，下载到 `$LFS/sources`，并完成 `md5sum` 校验，确认无缺漏。

---

## 0. 前置条件

* 已创建并挂载 **LFS 分区** 到 `/mnt/lfs`，并设置环境变量：

  ```bash
  export LFS=/mnt/lfs
  ```

---

## 1. 准备 `$LFS/sources` 目录

```bash
sudo mkdir -pv $LFS/sources
sudo chmod -v a+wt $LFS/sources  # sticky + 可写，便于后续下载
```

> sticky 位保证只有文件所有者才能删除自己放进去的文件。

---

## 2. 按官方 *wget-list* 精确下载 + 校验

> **优点**：只下需要的文件；可断点续传；严格对齐书本。这里把列表统一改写为 USTC 镜像直链。

```bash
# 2.1 获取列表与 md5sums（USTC 镜像）
wget -c -O md5sums https://mirrors.ustc.edu.cn/lfs/lfs-packages/12.3/md5sums

# 2.2 将列表中的每个 URL 改写为 USTC 的直链： https://mirrors.ustc.edu.cn/lfs/lfs-packages/12.3/<文件名>
sed -E 's|.*/([^/]+)$|https://mirrors.ustc.edu.cn/lfs/lfs-packages/12.3/\1|' wget-list-systemd > wget-list-ustc

# 2.3 下载（可多次执行，支持断点续传）
wget --input-file=wget-list-ustc --continue --show-progress --directory-prefix="$LFS/sources"

# 2.4 校验完整性
cp -v md5sums "$LFS/sources/"
pushd "$LFS/sources";md5sum -c md5sums;popd
```

## 3. 快速判断是否“有缺/有损坏”

```bash
cd "$LFS/sources"
# 列出缺失或校验失败的文件
md5sum -c md5sums 2>&1 | grep -E 'FAILED|No such file' || echo "All OK"

# 统计应有/已下载数量（以 md5sums 为准）
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

---

## 5. 一键脚本（可保存为 `fetch-lfs-sources.sh`）

```bash
#!/usr/bin/env bash
set -euo pipefail
: "${LFS:=/mnt/lfs}"
mkdir -p "$LFS/sources" && chmod a+wt "$LFS/sources"
cd /tmp
wget -c https://mirrors.ustc.edu.cn/lfs/lfs-packages/12.3/wget-list-systemd
wget -c -O md5sums https://mirrors.ustc.edu.cn/lfs/lfs-packages/12.3/md5sums
sed -E 's|.*/([^/]+)$|https://mirrors.ustc.edu.cn/lfs/lfs-packages/12.3/\1|' \
  wget-list-systemd | sort -u > wget-list-ustc
wget --input-file=wget-list-ustc --continue --show-progress \
     --directory-prefix="$LFS/sources"
cp -f md5sums "$LFS/sources/"
pushd "$LFS/sources" >/dev/null
if md5sum -c md5sums; then echo "\nAll files verified OK."; else echo "\nSome files missing or corrupted."; fi
popd >/dev/null
```

> 使用：`bash fetch-lfs-sources.sh`（确保 `$LFS` 已设置）。

---

完成后，`$LFS/sources` 目录应包含 LFS 12.3 所需的全部源码与补丁，`md5sum -c md5sums` 全部 `OK`，即可进入下一章的构建流程。
