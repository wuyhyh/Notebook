# 02-Git基础操作与提交规范

## 1 文档目标

本文用于帮助实习生掌握 Git 的基础操作，并理解项目开发中的基本提交规范。

学习完本文后，应能够：

1. 理解 Git 的基本作用。
2. 使用 `git clone` 获取项目代码。
3. 使用 `git status` 查看当前状态。
4. 使用 `git add` 和 `git commit` 提交修改。
5. 使用 `git log` 和 `git diff` 查看历史和差异。
6. 使用 `git pull` 和 `git push` 同步代码。
7. 编写清晰、规范的提交信息。
8. 避免常见的错误操作。

## 2 Git 是什么

## 2.1 基本概念

Git 是一个版本控制工具。

它可以帮助我们记录代码变化，并支持多人协作开发。

Git 可以回答这些问题：

1. 谁改了代码。
2. 改了哪些文件。
3. 每次修改的原因是什么。
4. 出问题后如何回退。
5. 多个人如何协作开发同一个项目。

## 2.2 Git 仓库

一个使用 Git 管理的项目称为仓库。

仓库中通常会有一个隐藏目录：

```text
.git/
```

这个目录保存了 Git 的版本历史和配置信息。

不要手动删除 `.git` 目录。

如果删除 `.git`，这个目录就不再是一个 Git 仓库。

## 2.3 本地仓库和远程仓库

常见情况：

1. 本地仓库：自己电脑上的代码仓库。
2. 远程仓库：GitLab、GitHub、Gitee 或公司服务器上的仓库。

常见协作流程：

1. 从远程仓库克隆代码。
2. 在本地修改代码。
3. 本地提交 commit。
4. 推送到远程仓库。
5. 其他人拉取更新。

## 3 Git 基本配置

## 3.1 配置用户名

第一次使用 Git 时，需要配置用户名：

```bash
git config --global user.name "Your Name"
```

示例：

```bash
git config --global user.name "zhangsan"
```

## 3.2 配置邮箱

```bash
git config --global user.email "your_email@example.com"
```

示例：

```bash
git config --global user.email "zhangsan@example.com"
```

## 3.3 查看配置

```bash
git config --list
```

也可以查看某一项：

```bash
git config user.name
git config user.email
```

## 4 获取项目代码

## 4.1 克隆仓库

使用 `git clone` 从远程仓库获取代码：

```bash
git clone <repo_url>
```

示例：

```bash
git clone https://example.com/project/demo.git
```

克隆完成后进入目录：

```bash
cd demo
```

## 4.2 查看远程仓库

```bash
git remote -v
```

常见输出：

```text
origin  https://example.com/project/demo.git (fetch)
origin  https://example.com/project/demo.git (push)
```

`origin` 是默认远程仓库名称。

## 5 查看仓库状态

## 5.1 git status

查看当前工作区状态：

```bash
git status
```

常见状态：

1. 没有修改。
2. 有文件被修改。
3. 有新文件未跟踪。
4. 有文件已经加入暂存区。
5. 当前分支是否领先或落后远程分支。

建议在每次提交前都执行：

```bash
git status
```

## 5.2 未跟踪文件

如果看到：

```text
Untracked files
```

说明这些文件还没有被 Git 管理。

如果需要加入版本控制，执行：

```bash
git add filename
```

如果是不应该提交的临时文件，应加入 `.gitignore`。

## 6 查看修改内容

## 6.1 查看未暂存修改

```bash
git diff
```

用于查看当前工作区中还没有 `git add` 的修改。

## 6.2 查看已暂存修改

```bash
git diff --cached
```

用于查看已经 `git add`、即将进入下一次提交的修改。

## 6.3 查看某个文件差异

```bash
git diff path/to/file.c
```

查看暂存区中的某个文件：

```bash
git diff --cached path/to/file.c
```

提交前建议至少执行：

```bash
git diff
git diff --cached
```

确认没有误提交无关修改。

## 7 添加修改

## 7.1 添加单个文件

```bash
git add filename
```

示例：

```bash
git add main.c
```

## 7.2 添加多个文件

```bash
git add main.c led.c led.h
```

## 7.3 添加当前目录所有修改

```bash
git add .
```

注意：`git add .` 会添加当前目录下所有修改和新增文件。

使用前应先执行：

```bash
git status
```

避免把临时文件、编译产物、日志文件提交进去。

## 7.4 取消暂存

如果文件已经 `git add`，但还不想提交，可以取消暂存：

```bash
git restore --staged filename
```

示例：

```bash
git restore --staged main.c
```

这不会丢失文件内容，只是从暂存区移出来。

## 8 提交修改

## 8.1 创建提交

```bash
git commit -m "commit message"
```

示例：

```bash
git commit -m "docs: add git basic usage guide"
```

提交会把暂存区中的内容记录为一个版本。

注意：只有 `git add` 过的内容才会进入提交。

## 8.2 提交前检查

提交前建议执行：

```bash
git status
git diff --cached
```

确认：

1. 提交的文件是否正确。
2. 修改内容是否完整。
3. 是否包含无关修改。
4. 是否包含密码、私钥、临时文件、编译产物。

## 8.3 修改最近一次提交信息

如果最近一次提交信息写错了，可以使用：

```bash
git commit --amend
```

或者：

```bash
git commit --amend -m "new commit message"
```

注意：如果这个提交已经推送到远程仓库，不要随意 amend，避免影响别人。

## 9 查看提交历史

## 9.1 git log

查看提交历史：

```bash
git log
```

常用简洁格式：

```bash
git log --oneline
```

示例输出：

```text
a1b2c3d docs: add git basic usage guide
e4f5g6h fix: correct uart init return value
```

## 9.2 查看最近几次提交

```bash
git log --oneline -5
```

表示只看最近 5 次提交。

## 9.3 查看某个文件历史

```bash
git log -- path/to/file.c
```

查看文件每次提交的具体变化：

```bash
git log -p -- path/to/file.c
```

## 10 分支基础

## 10.1 查看分支

```bash
git branch
```

查看本地和远程分支：

```bash
git branch -a
```

## 10.2 创建分支

```bash
git branch feature/demo
```

创建并切换到新分支：

```bash
git switch -c feature/demo
```

旧版本 Git 也常见：

```bash
git checkout -b feature/demo
```

## 10.3 切换分支

```bash
git switch main
```

或者：

```bash
git checkout main
```

## 10.4 分支命名建议

常见分支命名：

```text
feature/xxx
fix/xxx
docs/xxx
test/xxx
```

示例：

```text
feature/uart-driver
fix/gpio-init-error
docs/git-basic-guide
```

分支名应简短、清楚，能看出用途。

## 11 拉取和推送

## 11.1 拉取远程更新

```bash
git pull
```

常见含义：

1. 从远程仓库获取更新。
2. 合并到当前分支。

在开始工作前，建议先执行：

```bash
git pull
```

避免基于过旧代码开发。

## 11.2 推送本地提交

```bash
git push
```

如果是第一次推送新分支，可能需要：

```bash
git push -u origin feature/demo
```

含义：

1. 推送当前分支到远程仓库。
2. 建立本地分支和远程分支的跟踪关系。

## 11.3 推送前检查

推送前建议执行：

```bash
git status
git log --oneline -5
```

确认当前分支、提交内容和提交信息都正确。

## 12 撤销修改

## 12.1 撤销工作区修改

如果某个文件修改错了，想恢复到上一次提交状态：

```bash
git restore filename
```

示例：

```bash
git restore main.c
```

注意：这会丢弃当前未提交修改。

执行前要确认不再需要这些修改。

## 12.2 取消暂存

```bash
git restore --staged filename
```

这只取消 `git add`，不会丢弃文件内容。

## 12.3 删除未跟踪文件

查看将要删除的文件：

```bash
git clean -n
```

真正删除：

```bash
git clean -f
```

注意：`git clean -f` 会删除未被 Git 跟踪的文件，操作要谨慎。

## 13 .gitignore 文件

## 13.1 .gitignore 的作用

`.gitignore` 用于告诉 Git 哪些文件不需要纳入版本控制。

常见不应该提交的内容：

1. 编译产物。
2. 临时文件。
3. 日志文件。
4. IDE 本地配置。
5. 密码、私钥、token。
6. 大型生成文件。

## 13.2 C 项目常见 .gitignore

示例：

```text
*.o
*.a
*.so
*.d
*.out
app
build/
.cache/
*.log
```

如果使用 CLion、VS Code 等工具，还可以根据项目要求决定是否忽略：

```text
.idea/
.vscode/
```

注意：有些团队会提交 `.vscode/settings.json` 作为共享配置，具体以项目规则为准。

## 13.3 已经被跟踪的文件不会自动忽略

如果文件已经被 Git 跟踪，后来加入 `.gitignore` 不会自动停止跟踪。

需要执行：

```bash
git rm --cached filename
```

示例：

```bash
git rm --cached app
```

然后提交 `.gitignore` 和这次删除跟踪记录。

## 14 提交信息规范

## 14.1 为什么提交信息很重要

好的提交信息可以让别人快速理解：

1. 这次改了什么。
2. 为什么要改。
3. 影响范围是什么。
4. 是否和某个 bug、任务、需求有关。

不好的提交信息：

```text
update
fix
修改
临时提交
```

这些信息几乎没有价值。

## 14.2 推荐格式

推荐使用类似格式：

```text
type: summary
```

示例：

```text
fix: correct uart baudrate register mask
docs: add makefile basic guide
feat: add gpio led control interface
refactor: split uart register definitions
```

## 14.3 常见 type

常见类型：

```text
feat      新功能
fix       修复问题
docs      文档修改
style     代码格式修改，不影响逻辑
refactor  重构，不新增功能，也不修复 bug
test      测试相关修改
build     构建系统或依赖修改
chore     杂项维护
```

示例：

```text
docs: add git basic usage guide
fix: handle null pointer in led_init
build: add makefile for demo project
```

## 14.4 summary 写法建议

summary 建议：

1. 使用简短英文或清晰中文。
2. 说明具体修改内容。
3. 不要太笼统。
4. 不要写句号结尾。
5. 尽量控制在一行内。

推荐：

```text
fix: correct gpio direction check
docs: add gcc compile flow note
feat: add uart send buffer helper
```

不推荐：

```text
fix bug
update code
modify files
```

## 14.5 中文提交信息可以吗

可以，但要清晰具体。

推荐：

```text
docs: 增加 Git 基础操作文档
fix: 修正 UART 波特率掩码错误
build: 增加示例工程 Makefile
```

不推荐：

```text
修改
更新
修一下
```

如果团队没有特别要求，建议 type 使用英文，summary 可以中文。

## 15 提交粒度

## 15.1 一次提交只做一类事情

推荐：

```text
docs: add git basic usage guide
```

这次提交只修改文档。

不推荐一次提交同时包含：

1. 文档修改。
2. 代码重构。
3. bug 修复。
4. 临时调试代码。
5. 格式化大量无关文件。

这样会导致代码审查和问题回退都很困难。

## 15.2 提交前自查

提交前问自己：

1. 这次提交的目的是否明确？
2. 文件是否都是相关修改？
3. 是否包含临时调试代码？
4. 是否包含编译产物？
5. 是否包含密码、私钥、token？
6. 提交信息是否能让别人看懂？

## 16 常见工作流程

## 16.1 修改文档流程

```bash
git pull
git status
vim docs/git-basic.md
git diff
git add docs/git-basic.md
git diff --cached
git commit -m "docs: add git basic usage guide"
git push
```

## 16.2 修改代码流程

```bash
git pull
git switch -c fix/led-init
vim led.c
make
git status
git diff
git add led.c
git diff --cached
git commit -m "fix: correct led init return value"
git push -u origin fix/led-init
```

## 16.3 查看自己改了什么

```bash
git status
git diff
```

查看已经加入暂存区的内容：

```bash
git diff --cached
```

查看最近提交：

```bash
git log --oneline -5
```

## 17 常见错误

## 17.1 忘记 git add

现象：

```bash
git commit -m "fix: update led"
```

结果提示没有内容可提交。

原因是修改还没有加入暂存区。

解决：

```bash
git add led.c
git commit -m "fix: update led"
```

## 17.2 提交了编译产物

例如误提交：

```text
*.o
app
build/
```

解决：

1. 更新 `.gitignore`。
2. 从 Git 跟踪中移除编译产物。

```bash
git rm --cached app
git rm --cached *.o
```

然后提交：

```bash
git add .gitignore
git commit -m "chore: ignore build outputs"
```

## 17.3 在错误分支上修改

先查看当前分支：

```bash
git branch
```

如果已经在错误分支上修改了，但还没有提交，可以先暂存：

```bash
git stash
```

切换到正确分支：

```bash
git switch correct-branch
```

恢复修改：

```bash
git stash pop
```

## 17.4 盲目使用 git add .

`git add .` 很方便，但容易误加无关文件。

建议执行前先看：

```bash
git status
```

更稳妥的方式是只添加相关文件：

```bash
git add main.c led.c
```

## 17.5 随意强制推送

不要随意执行：

```bash
git push --force
```

强制推送可能覆盖远程分支历史，影响其他人。

除非你明确知道后果，并且已经和团队成员确认，否则不要使用。

## 18 常用命令速查

## 18.1 查看类

```bash
git status
git log --oneline
git diff
git diff --cached
git branch
git remote -v
```

## 18.2 提交流程类

```bash
git add filename
git commit -m "type: summary"
git push
```

## 18.3 同步类

```bash
git pull
git fetch
```

## 18.4 分支类

```bash
git branch
git switch branch_name
git switch -c new_branch
```

## 18.5 撤销类

```bash
git restore filename
git restore --staged filename
git clean -n
git clean -f
```

## 19 简单练习

## 19.1 初始化练习仓库

```bash
mkdir git-demo
cd git-demo
git init
```

创建文件：

```bash
echo "hello git" > README.md
```

查看状态：

```bash
git status
```

提交：

```bash
git add README.md
git commit -m "docs: add readme"
```

查看历史：

```bash
git log --oneline
```

## 19.2 修改文件并查看差异

修改 `README.md`：

```bash
echo "second line" >> README.md
```

查看差异：

```bash
git diff
```

加入暂存区：

```bash
git add README.md
```

查看暂存差异：

```bash
git diff --cached
```

提交：

```bash
git commit -m "docs: update readme"
```

## 19.3 .gitignore 练习

创建编译产物：

```bash
touch main.o app
```

创建 `.gitignore`：

```bash
cat > .gitignore << 'EOF'
*.o
app
EOF
```

查看状态：

```bash
git status
```

提交 `.gitignore`：

```bash
git add .gitignore
git commit -m "chore: add gitignore"
```

## 20 小结

Git 是项目协作和版本管理的基础工具。

需要重点记住：

1. `git clone` 用于获取远程仓库。
2. `git status` 用于查看当前状态。
3. `git diff` 用于查看未暂存修改。
4. `git diff --cached` 用于查看已暂存修改。
5. `git add` 用于加入暂存区。
6. `git commit` 用于创建提交。
7. `git log --oneline` 用于查看提交历史。
8. `git pull` 用于拉取远程更新。
9. `git push` 用于推送本地提交。
10. `git switch -c` 用于创建并切换分支。
11. `.gitignore` 用于忽略不需要提交的文件。
12. 提交信息要清楚，不能只写 `update`、`fix`、`修改`。
13. 一次提交尽量只做一类事情。
14. 不要提交编译产物、临时文件、密码、私钥和 token。
15. 不要随意使用 `git push --force`。

掌握 Git 基础后，才能比较顺畅地参与多人项目开发、代码审查和版本发布流程。
