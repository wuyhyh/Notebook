## `git reset` 和 `git checkout` 的使用及区别

在 Git 中，`git reset` 和 `git checkout` 都用于**改变工作目录的状态**，但它们的用途和影响范围不同。

### **1. `git reset` 用于重置提交和暂存区**

`git reset` 用于重置 Git 历史，可以修改**提交记录（commit）**、**暂存区（staging area）** 和 **工作区（working directory）**
。它常用于**撤销提交**、**恢复文件到某个历史状态**。

#### **（1）基本用法**

```bash
git reset [选项] <commit>
```

其中 `<commit>` 可以是：

- `HEAD~1`（上一个提交）
- `HEAD~2`（上上个提交）
- 提交哈希值（如 `a1b2c3d4`）

#### **（2）`git reset` 的三种模式**

`git reset` 提供 **soft（软重置）、mixed（默认）、hard（硬重置）** 三种模式，它们的影响范围不同。

| 模式            | 作用                  | 提交记录（commit） | 暂存区（index） | 工作区（working directory） |
|---------------|---------------------|--------------|------------|------------------------|
| `--soft`      | 仅重置提交记录，保留修改        | **回退**       | **不变**     | **不变**                 |
| `--mixed`（默认） | 回退提交，同时取消 `git add` | **回退**       | **重置**     | **不变**                 |
| `--hard`      | 回退提交，撤销所有修改         | **回退**       | **重置**     | **重置**                 |

---

#### **（3）具体示例**

##### **① `--soft`：回退提交，但保留修改**

```bash
git reset --soft HEAD~1
```

- **提交记录被回退**，但文件仍然保留在**暂存区**和**工作区**。
- 适用于：如果你提交了代码但发现还需要再修改，可以用 `--soft` 回退提交，而不会影响你的修改。

##### **② `--mixed`（默认）：回退提交，并取消 `git add`**

```bash
git reset HEAD~1
```

等同于：

```bash
git reset --mixed HEAD~1
```

- **提交记录被回退**，**暂存区被清空**，但**工作区文件仍然保留**。
- 适用于：如果你提交了代码但不想提交其中的一部分，可以用 `--mixed` 取消 `git add`，然后重新 `git add` 需要的文件。

##### **③ `--hard`：回退提交，并丢弃所有修改**

```bash
git reset --hard HEAD~1
```

- **提交记录被回退**，**暂存区和工作区都恢复到指定提交的状态**。
- **不可逆**，如果你没有备份，修改的文件将会丢失。
- 适用于：如果你想彻底回滚到某个历史版本，并放弃所有未提交的更改。

---

### **2. `git checkout` 用于切换分支或恢复文件**

`git checkout` 主要用于**切换分支**或**恢复单个文件到某个历史版本**。

#### **（1）切换分支**

```bash
git checkout branch-name
```

- 这个命令会切换到 `branch-name` 分支。

如果你当前有未提交的修改，Git 可能会提示你不能切换分支。可以用 `stash` 先保存修改：

```bash
git stash
git checkout branch-name
git stash pop  # 恢复修改
```

#### **（2）恢复文件**

如果你想恢复某个文件到最新的提交状态，可以使用：

```bash
git checkout -- filename
```

- 这个命令会将 `filename` 还原到**当前分支最后一次提交的状态**。
- 如果 `filename` 只是被修改但没有 `git add`，这个命令可以丢弃修改。
- **如果已经 `git add`，但还没有 `commit`，这个命令不会影响文件**。

如果你想恢复文件到某个旧版本：

```bash
git checkout <commit> -- filename
```

例如：

```bash
git checkout HEAD~2 -- myfile.txt
```

- 这会把 `myfile.txt` 恢复到 **两次提交之前的版本**，但不会影响其他文件。

---

### **3. `git reset` 和 `git checkout` 的区别**

| 操作       | `git reset`             | `git checkout`      |
|----------|-------------------------|---------------------|
| 主要作用     | 撤销提交、撤销 `git add`、清理工作区 | 切换分支、恢复文件           |
| 影响对象     | 整个分支或多个文件               | 具体文件或整个分支           |
| 是否影响提交历史 | 可能影响（软、混合、硬）            | 不影响                 |
| 是否影响工作区  | `--hard` 会影响            | 只影响被 `checkout` 的文件 |

---

### **4. 什么时候用 `git reset`，什么时候用 `git checkout`？**

#### **使用 `git reset` 的情况**

1. **想撤销最近的提交，但保留文件修改**
   ```bash
   git reset --soft HEAD~1
   ```
2. **想撤销 `git add`（但不撤销文件修改）**
   ```bash
   git reset HEAD filename
   ```
3. **想彻底回滚到某个历史版本**
   ```bash
   git reset --hard commit-hash
   ```

#### **使用 `git checkout` 的情况**

1. **切换分支**
   ```bash
   git checkout develop
   ```
2. **恢复文件到上一次提交的状态**
   ```bash
   git checkout -- filename
   ```
3. **恢复文件到某个历史版本**
   ```bash
   git checkout commit-hash -- filename
   ```

---

### **5. `git switch`（替代 `git checkout` 切换分支）**

在 Git 2.23 之后，官方推荐使用 `git switch` 替代 `git checkout` 来切换分支：

- 切换分支：
  ```bash
  git switch branch-name
  ```
- 创建并切换到新分支：
  ```bash
  git switch -c new-branch
  ```

但 `git checkout` 仍然可以用来**恢复文件**，所以 `git checkout` 仍然是一个重要的命令。

---

## **6. 总结**

| 命令                                     | 作用                     | 影响范围           |
|----------------------------------------|------------------------|----------------|
| `git reset --soft HEAD~1`              | 取消最近一次提交，保留修改          | 仅影响提交记录        |
| `git reset --mixed HEAD~1`             | 取消最近一次提交，并撤销 `git add` | 影响提交记录和暂存区     |
| `git reset --hard HEAD~1`              | 彻底回退到上一个提交，丢弃所有修改      | 影响提交记录、暂存区、工作区 |
| `git checkout branch-name`             | 切换到指定分支                | 影响当前 HEAD      |
| `git checkout -- filename`             | 丢弃某个文件的本地修改            | 仅影响指定文件        |
| `git checkout commit-hash -- filename` | 将文件恢复到某个提交的状态          | 仅影响指定文件        |
| `git switch branch-name`               | 切换到分支（推荐方式）            | 影响当前 HEAD      |

---

### **7. 结论**

- **如果你想撤销提交，但保留文件，使用 `git reset --soft`。**
- **如果你想完全回退到某个提交，使用 `git reset --hard`（危险操作）。**
- **如果你只是想恢复某个文件，使用 `git checkout -- filename`。**
- **如果你想切换分支，使用 `git checkout branch-name` 或 `git switch branch-name`。**
