# `git rebase -i` 交互式变基详解

`git rebase -i`（交互式变基）是 Git 提供的一种强大的工具，允许你在变基时**修改、合并、删除、重排**提交记录，使你的 Git
提交历史更加清晰和整洁。

---

## 1. `git rebase -i` 的作用

使用 `git rebase -i`，你可以：

- **合并多个提交**（squash）
- **修改某个提交的提交信息**
- **删除某个提交**
- **重新排序提交**
- **拆分提交**
- **修改提交的内容**

---

## 2. `git rebase -i` 的基本用法

### **（1）启动交互式变基**

```bash
git rebase -i HEAD~N
```

- `N` 表示要变基的提交数量，例如 `git rebase -i HEAD~5` 表示对最近的 5 个提交进行交互式变基。

或者，变基到某个特定的提交：

```bash
git rebase -i <commit-hash>
```

> 这里的 `<commit-hash>` 是变基到的目标提交，它不会被修改，**变基操作将影响这个提交之后的所有提交**。

---

### **（2）进入交互式编辑界面**

运行 `git rebase -i HEAD~3` 后，你会进入一个文本编辑界面，类似于：

```plaintext
pick 1234567 修复了登录 bug
pick abcdefg 优化了 UI 代码
pick 89abcde 添加了单元测试

# Rebase 89abcde onto 7654321 (3 commands)
#
# Commands:
#  pick = 保留这个提交 (默认)
#  reword = 修改提交信息
#  edit = 修改提交内容
#  squash = 合并到上一个提交 (压缩)
#  fixup = 与上一个提交合并，但丢弃提交信息
#  drop = 删除这个提交
#
```

---

## 3. `git rebase -i` 的常见操作

### **（1）合并多个提交（Squash）**

如果你想将多个提交合并成一个，可以使用 `squash`（缩写 `s`）。

#### **操作**

修改文件，将：

```plaintext
pick 1234567 修复了登录 bug
pick abcdefg 优化了 UI 代码
pick 89abcde 添加了单元测试
```

改成：

```plaintext
pick 1234567 修复了登录 bug
squash abcdefg 优化了 UI 代码
squash 89abcde 添加了单元测试
```

#### **效果**

- `abcdefg` 和 `89abcde` 会合并到 `1234567` 这个提交中。
- 变基过程中，Git 会弹出一个新的编辑窗口，让你修改合并后的提交信息。

如果你希望合并多个提交，但不想修改提交信息，可以使用 `fixup`，例如：

```plaintext
pick 1234567 修复了登录 bug
fixup abcdefg 优化了 UI 代码
fixup 89abcde 添加了单元测试
```

这样 `abcdefg` 和 `89abcde` 会合并到 `1234567`，**但不会修改提交信息**。

---

### **（2）修改提交信息（Reword）**

如果你想修改某个提交的提交信息，可以使用 `reword`（缩写 `r`）。

#### **操作**

将：

```plaintext
pick 1234567 修复了登录 bug
```

改成：

```plaintext
reword 1234567 修复了登录 bug
```

#### **效果**

- 变基时 Git 会弹出一个编辑框，让你修改 `1234567` 这个提交的提交信息。

---

### **（3）修改提交内容（Edit）**

如果你想修改某个提交的内容，可以使用 `edit`。

#### **操作**

将：

```plaintext
pick 1234567 修复了登录 bug
```

改成：

```plaintext
edit 1234567 修复了登录 bug
```

#### **效果**

- Git 会暂停变基，并让你回到这个提交的状态。
- 你可以使用 `git commit --amend` 修改提交内容。
- 然后使用：
  ```bash
  git rebase --continue
  ```
  继续变基。

---

### **（4）删除提交（Drop）**

如果你想删除某个提交，可以使用 `drop`。

#### **操作**

将：

```plaintext
pick abcdefg 优化了 UI 代码
```

改成：

```plaintext
drop abcdefg 优化了 UI 代码
```

#### **效果**

- `abcdefg` 这个提交会被删除，其他提交不会受到影响。

---

### **（5）重新排序提交**

你可以直接调整行的顺序来改变提交的顺序。例如：

#### **原始顺序**

```plaintext
pick 1234567 修复了登录 bug
pick abcdefg 优化了 UI 代码
pick 89abcde 添加了单元测试
```

#### **修改后的顺序**

```plaintext
pick 89abcde 添加了单元测试
pick abcdefg 优化了 UI 代码
pick 1234567 修复了登录 bug
```

#### **效果**

- `89abcde` 现在成为最早的提交，`1234567` 变成了最新的提交。

---

## 4. 变基冲突处理

在变基过程中，如果发生冲突，Git 会暂停变基，并提示你手动解决冲突。例如：

```bash
error: could not apply abcdefg... 优化了 UI 代码
```

#### **解决方法**

1. **打开冲突文件**，手动解决冲突：
   ```bash
   git status
   ```
   会显示哪些文件有冲突。

2. **解决冲突后，添加修改**：
   ```bash
   git add <resolved-file>
   ```

3. **继续变基**：
   ```bash
   git rebase --continue
   ```

4. 如果你想放弃变基，可以使用：
   ```bash
   git rebase --abort
   ```

---

## 5. 变基后推送远程仓库

如果你已经将变基后的分支推送到远程，并且别人已经基于这个分支进行开发，变基会**重写提交历史**，导致推送失败。

如果你仍然要推送（请谨慎），需要使用 `--force-with-lease`：

```bash
git push --force-with-lease origin branch-name
```

如果你确定不会影响他人，可以使用（更危险）：

```bash
git push --force origin branch-name
```

**⚠️ `--force` 可能导致他人的工作丢失，建议使用 `--force-with-lease` 以确保安全！**

---

## 6. 总结

| 任务     | 交互式变基命令                       |
|--------|-------------------------------|
| 合并多个提交 | `squash` or `fixup`           |
| 修改提交信息 | `reword`                      |
| 修改提交内容 | `edit`                        |
| 删除提交   | `drop`                        |
| 重新排序提交 | 调整行顺序                         |
| 处理冲突   | 手动解决后 `git rebase --continue` |
| 取消变基   | `git rebase --abort`          |

---

### 7. 什么时候使用 `git rebase -i`？

- **整理本地提交**：在推送代码之前，清理不必要的提交，合并小的提交。
- **改进提交信息**：确保提交信息清晰、规范。
- **删除错误的提交**：如果你误提交了一些无关的更改，可以在变基时删除它们。

---
