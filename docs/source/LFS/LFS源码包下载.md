# LFS 源码包下载与校验（USTC 镜像）

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
