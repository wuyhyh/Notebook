# openeuler 5.10.136 内核与 iso-136 内核差异对比

行，这个思路很对：**以 openEuler 136.12.0 为干净基线，按你可控的节奏把 iso-136 的改动“挑拣+分组+可回滚地”移植过来**
。关键是流程要保证：每一步都能对比、能回滚、能定位“哪一组改动导致不稳定”。

下面给你一套不复杂、但足够严谨的流程（命令 + 分支组织 + CLion 配合）。

---

## 0. 目标产物与分支约定

你最终要得到：

* `release/oe-136.12.0`：**你的稳定发布分支**（最终稳定内核在这）
* `work/port-iso136`：**移植工作分支**（日常操作、反复试）
* `audit/iso136`（可选）：仅用于统计、记笔记（不改代码也行）

来源锚点保持不动：

* `base/oe-136.12.0`（openEuler 干净基线）
* `base/iso-136`（飞腾 ISO 提取基线）

---

## 1. 准备阶段（一次性做完）

### 1.1 确保 iso 分支干净（至少清掉垃圾文件）

你已经发现 `drivers/acpi/irq.c.rej` 这种残留。你要先在 `base/iso-136` 的“复制分支”上清掉，避免后面移植被噪音干扰：

```bash
git switch base/iso-136
git switch -c cleanup/iso-136

# 清掉 rej/orig/bak 这类文件（先列出来确认）
git ls-files | grep -E '\.(rej|orig|bak)$' || true

# 逐个删除（至少先删 irq.c.rej）
git rm -f drivers/acpi/irq.c.rej
git commit -m "cleanup: remove patch reject artifacts"

# 以后对比都用 cleanup/iso-136 代替 base/iso-136
```

> 之后你所有 diff 都以 `cleanup/iso-136` 为“飞腾侧参考树”。

---

## 2. 建立你的 release 分支与工作分支

### 2.1 从 openEuler 基线创建 release

```bash
git switch base/oe-136.12.0
git switch -c release/oe-136.12.0
```

### 2.2 从 release 派生移植工作分支

```bash
git switch release/oe-136.12.0
git switch -c work/port-iso136
```

以后你所有移植都在 `work/port-iso136` 上做；`release/oe-136.12.0` 只在“你确认稳定”后再 fast-forward 或 merge（推荐 FF）。

---

## 3. 核心方法：把 iso 的改动分组，按“特性桶”逐步移植

你不要追求“一次把 iso 全搬过来”，要按桶来（每桶一个或几个 commit），这样你能回滚/二分定位。

我建议桶顺序如下（从“最必要 + 最容易验证”到“风险大”）：

### 桶 A：板级 DTS（必要，且最贴你自研板）

* `arch/arm64/boot/dts/phytium/`
* `arch/arm64/boot/dts/Makefile`（注意别把无关板子也引入）
* 如果你的自研板 dts 在别处，也一起纳入

### 桶 B：Kconfig/defconfig（控制开关，决定行为）

* `arch/arm64/configs/phytium_defconfig`
* `arch/arm64/configs/defconfig`
* 以及涉及到的 `Kconfig` 变更

### 桶 C：PCIe RC/EP + MSI + quirks（高风险，但你必须面对）

* `drivers/pci/`、`drivers/pci/controller/`、`drivers/pci/msi.c`、`probe.c`、`quirks.c`

### 桶 D：IOMMU/SMMU（高风险，常导致随机崩）

* `drivers/iommu/*`

### 桶 E：平台外设驱动（多数不是启动必需）

USB/DRM/声卡/杂项等，放到最后。

---

## 4. 每个桶的移植动作（标准作业流程）

对每个桶都按这个“循环”做：

### 4.1 看差异（只看这个桶）

```bash
git diff release/oe-136.12.0..cleanup/iso-136 -- <PATH1> <PATH2> ...
```

### 4.2 应用差异（推荐用 3-way checkout，最省事）

在 `work/port-iso136` 分支上：

**方式 1：直接把 iso 的版本“检出覆盖”到当前分支（最简单）**

```bash
git switch work/port-iso136

# 例如 DTS 桶
git checkout cleanup/iso-136 -- arch/arm64/boot/dts/phytium arch/arm64/boot/dts/Makefile
```

**方式 2：用 CLion 手工挑 hunk（更精细）**

* 在 CLion Compare 里只把你要的 hunk 应用过来（适合 PCIe/MSI 这种你想“挑改动”的）

### 4.3 做一次“桶内自检”

* `git status` 确认只动了你预期的目录
* `git diff` 复查没有夹带 `.gitignore` 这种噪音

### 4.4 提交（一个桶一个 commit 或小串 commit）

```bash
git add <paths...>
git commit -m "port(iso-136): <feature bucket name>"
```

### 4.5 编译 + 启动验证（你自己的最小验证集）

建议你固定一个最小验证清单，保证每次可比：

* 编译成功（Image/dtb/modules）
* 启动到用户态（或至少 initramfs）
* 基础硬件：串口、rootfs、NVMe、网卡（你最常踩的）
* 如果你有固定压测：跑 5~10 分钟就够（先别追求 300s openssl 那种）

### 4.6 如果炸了：立刻二分定位

因为你按桶提交了，所以很好处理：

* 先 `git revert <commit>` 看是否恢复稳定
* 或者在桶内拆分更细 commit（PCIe/MSI/IOMMU 很可能需要拆）

---

## 5. 把 work 分支推进到 release（只在稳定节点推进）

当你完成若干桶，并且你认为“这一组合已经稳定”：

```bash
git switch release/oe-136.12.0
git merge --ff-only work/port-iso136
```

> 只用 `--ff-only` 的好处：release 分支历史永远是线性的、可回溯、可 bisect。

---

## 6. 你要“复现飞腾干过的工作”：怎么让结果更像他们？

你最终想“复现飞腾的人做过的工作”，不是简单复制文件，而是复制**改动集合与顺序**。建议你在每个桶提交里写清楚：

* 来自 `cleanup/iso-136` 的哪些文件
* 是否做了“只移植子集”的裁剪
* 关联的配置项变化（尤其是 defconfig）

最轻量的记录方式：

* 每个桶 commit message 里附上关键文件列表
* 或者在仓库加一个 `docs/porting/iso-136.md` 记流水账（每次追加一段）

---

## 7. CLion 的最佳用法（让移植“可视化”）

你就用 CLion 做两件事：

1. **Compare `work/port-iso136` vs `cleanup/iso-136`**
   看你还差哪些没移植（你会越来越接近 iso）

2. **Compare `work/port-iso136` vs `release/oe-136.12.0`**
   看你当前引入了哪些改动（用于 review 和写 commit）

对于 PCIe/MSI/IOMMU 这种容易“只挑一部分”的目录，用 CLion 的 diff/hunk apply 会比命令行舒服。

---

## 8. 最关键的纪律（决定你能不能得到“稳定内核”）

* 永远不要一次性引入太多（尤其 PCIe/MSI/IOMMU 一把梭）
* 每个桶提交后都要能启动/复测
* 有问题先回滚，再把桶拆小
* release 分支只吸收“你确认稳定”的节点（FF-only）

---

如果你愿意，我可以再把“桶 A~E”细化成一个**实际的移植顺序清单**（每桶具体到路径、以及你优先该挑哪些文件），你只要告诉我：
你自研板启动主要走 **DT 还是 ACPI**？（大概率 DT）以及你的 PCIe 拓扑是否有交换芯片（你之前提过有）。我会按这个给你“最短稳定路径”。


# 差异清单

```text
[wuyuhang@Tokamark-2 openeuler-fusion]$ git diff --name-only release/oe-136.12.0..cleanup/iso-136 > /tmp/iso136.todo
[wuyuhang@Tokamark-2 openeuler-fusion]$ wc -l /tmp/iso136.todo
563 /tmp/iso136.todo
[wuyuhang@Tokamark-2 openeuler-fusion]$
```


