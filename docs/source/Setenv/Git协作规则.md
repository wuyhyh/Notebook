# Git 协作规则（仅 push + 本地集成，master 永远线性）

## 1. 目标

* `master` 分支保持严格线性历史（Linear History）
* 团队成员只在自己的分支上提交与推送，不直接改动 `master`
* Maintainer 在本地做集成，然后 fast-forward 推送到 `master`
* 当前项目为文档协作，不要求构建/测试验证

## 2. 分支约定

### 2.1 主分支

* `master`：仅 Maintainer 可推送
* `master` 合并策略：只允许 fast-forward（禁止 merge commit）
* 禁止对 `master` force push

### 2.2 个人分支

* 每位成员维护自己的远端分支（示例）：

    * `ljc/dev`
    * `zpc/dev`
* 成员分支允许持续累积提交，用于文档协作

## 3. 成员（实习生/开发者）操作规范

### 3.1 第一次创建个人分支（只做一次）

```bash
git fetch origin
git checkout -b ljc/dev origin/master
git push -u origin ljc/dev
```

### 3.2 每天开始工作前同步 master（每天重复）

只允许用 merge 同步，禁止 rebase：

```bash
git checkout ljc/dev
git fetch origin
git merge origin/master
git push
```

### 3.3 编辑文档、提交、推送

```bash
git add -A
git commit -m "doc: 简短说明修改内容"
git push
```

提交信息建议：

* 统一用 `doc:` 前缀（例如 `doc: fix section 2.4 translation`）
* 一次提交只做一类修改（便于回滚）

## 4. Maintainer（吴宇航）本地集成到 master 流程

目标：不改动成员远端分支历史，但 `master` 仍严格线性。

以集成 `origin/ljc/dev` 为例：

### 4.1 更新本地 master

```bash
git fetch origin
git checkout master
git pull --ff-only
```

### 4.2 从成员分支创建本地临时集成分支

```bash
git checkout -b int/ljc-dev origin/ljc/dev
```

### 4.3 在临时分支上 rebase 到 master（只改你本地，不碰远端）

```bash
git rebase master
```

如果有冲突：

```bash
# 解决冲突后
git add <冲突文件>
git rebase --continue
```

放弃本次集成：

```bash
git rebase --abort
```

### 4.4 fast-forward 合入 master（保证 master 无 merge commit）

```bash
git checkout master
git merge --ff-only int/ljc-dev
```

### 4.5 推送 master

```bash
git push origin master
```

### 4.6 删除本地临时分支（推荐）

```bash
git branch -D int/ljc-dev
```

说明：

* 你可以对本地临时分支 rebase 来“洗线性”
* 但绝不对 `origin/ljc/dev` 做 rebase 并推回去

## 5. 禁令（必须遵守）

### 5.1 成员分支禁止 rebase 后强推

成员分支（如 `origin/ljc/dev`）一旦 push 过：

* 禁止 `git pull -r`
* 禁止 `git rebase ...` 后 `git push --force` / `--force-with-lease`

原因：会重写历史，导致你本地集成和其他成员同步都变复杂。

### 5.2 master 禁止 force push

* 禁止对 `master` 使用 `git push --force` / `--force-with-lease`
* 原因：团队协作基线会被破坏

### 5.3 master 禁止 merge commit

* `master` 只允许 `git merge --ff-only ...`
* 不允许出现 `Merge branch ...` 这种提交

## 6. 常用检查命令

查看分支图（确认 master 线性）：

```bash
git log --graph --oneline --decorate --all --date-order
```

查看远端分支：

```bash
git branch -r
```

---

如果你愿意再进一步“把规则落到 GitLab 权限配置”，我建议你做两件事（不需要 MR，也能生效）：

* 把 `master` 设为 Protected Branch：只允许 Maintainer push
* 关闭/限制对 `master` 的 force push

现在这套流程已经足够稳定，后面要引入代码协作和验证，再把第 4.3 和 4.4 中间插入“构建/格式检查/链接检查”即可。

