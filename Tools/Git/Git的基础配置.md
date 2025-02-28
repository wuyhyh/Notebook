# 使用 Git 足够的特性

简单的设计可能就是最好的设计，就像铲子被发明和使用了几千年。

但是 Git 这个工具有些功能强大且复杂没用。

---

## Git 安装与初始化

- 在 Fedora 上安装 Git

```shell
sudo dnf install git -y
```

- 在 Ubuntu 上安装 Git

```shell
sudo apt install git -y
```

- 配置用户名和邮箱

```shell
git config --global user.name <name>
git config --global user.email <email_address>
```

比如：

```shell
git config --global user.name "wuyhyh"
git config --global user.email wuyhyh@gmail.com
```

- 查询配置信息

```shell
git config --list
```

配置信息是可以在子目录下多次新建的，配置信息保存在文件`.gitconfig下`。子目录的配置会覆盖顶层目录的配置。

- 在服务器的`~/.ssh`目录下生成公钥和私钥

```shell
cd ~/.ssh;ssh-keygen
```

- 复制公钥到 github 端

## Git 的基本用法

### 1. 创建 Git 仓库

- 在现有的项目根目录下进行初始化

```shell
git init
```

- Clone 远程仓库

```shell
git clone <URL>
```

你还可以修改 clone 下来的仓库的默认名称，但是没有什么卵用。

### 2. Git 的基本模型

Git 本质上是一个按内容寻址的文件系统。所有 Git 中的对象都是通过20个字节，160个`ASCII`字符的`sha-1`的序列来索引的。
不用担心这个索引会出现冲突，这个地址空间非常的大。

#### Git 中有三个区域:

- 已经 commit 的文件，被压缩后放置在`.git`目录下。`HEAD`是一个指针，指向最后定型的提交的`sha-1`值.
- 已经 index 的文件，也就是已经暂存的文件，这些文件可以理解为登记造册的文件，下一次提交会把他们放入commit区。
- 工作区，这个区域的文件可以是刚刚新增的，亦可以是以前就在的，以前就有的文件可能是被修改了的，也可以是没有没修改过的。
  所以就有了tracked untracked modified unmodified 的概念。

### 3. 文件状态的基本操作

查看当前文件的状态

```shell
git status
```

把文件从工作区域移动到暂存区

```shell
git add <file_name or dir_name>
git add . # 当前 tracked 的所有文件
```

相反的，可以将文件从暂存区移动回工作区

```shell
git reset HEAD~
```

放弃对某个文件或者所有文件的修改，还原到上次`commit`的状态

```shell
git checkout -- <filename>
```

还可以查看一下现在暂存区的文件和已经持久化的文件有什么区别，也就是下一次提交会产生什么后果：

```shell
git diff
```

提交代码，进行持久化

```shell
git commit -m <message>
```

不再跟踪某个文件

```shell
git rm --cached <file_name>
```

删除文件还是交给 `rm -rf` 去做吧。

查看历史提交

```shell
git log
git log --pretty=oneline # 有用但是那么长，傻逼
```

如果刚刚提交的内容不满意，可以修改`commit message`，还可以追加文件

```shell
git commit --amend
```

如果你已经把`commit`推送到了远端仓库，那么再次推送，要加上`force`

```shell
git push <remote_rep_name> <remote_branch_name> -f
```

比如

```shell
git push origin master -f
```

### 4. 远程仓库的使用

使用`git clone`得到的仓库默认其远程仓库是`origin`

显示远程仓库

```shell
git remote
git remote -v # 还会显示 URL
```

远程仓库的添加、删除、查看、重命名

```shell
git remote add <rep_name> <url>
git remote rm <rep_name>
git remote show <rep_name>
git remote rename <old_name> <new_name>
```

从远程仓库拉去数据，`fetch`只会取回本地没有的数据，不会修改本地工作目录下的数据。

```shell
git fetch <remote_rep_name>
```

把数据推送到远端

```shell
git push <remote_rep_name> <remote_branch_name>
```

比如

```shell
git push origin master
```

### 5. 打标签

标签本质上是一个`sha-1`的别名，可以通过标签来区别`commit`，

例举标签

```shell
git tag          # 显示所有标签
git tag -l "v1.*"  # 显示匹配 v1.* 模式的标签
```

根据某次`commit`创建注释标签

```shell
git tag -a v1.0 9fceb02 -m "对某个历史提交打标签"
```

删除标签

```shell
git tag -d v1.0
git push origin --delete tag v1.0 # 删除远程标签
```

查看标签信息

```shell
git show v1.4
```

将标签推送到远程服务器上

```shell
git push origin v1.0 #推送某一个标签
git push origin --tags # 推送所有标签
```

## Git 的分支特性

分支的本质是指向某个`commit`的指针。
创建一个新的分支本质上，是创建一个新的可移动的指针。

`master` 分支和其他分支没有任何区别，就像 `origin` 仓库名和其他仓库名没有任何区别

`HEAD` 是一个特殊的指针，指向当前所在的本地分支。

切换分支的时候，对应的工作目录中的文件内容也会改变。

查看分支

```shell
git branch -v # 列举本地分支
git branch -r # 查看远程分支
git branch -a # 查看本地和远程所有分支
git branch | grep <feature> # 过滤分支
```

创建分支

```shell
git branch <new_branch_name> # 创建分支
git checkout <branch_name> # 切换到已有的分支
```

创建一个新分支并且切换过去是一个常用的命令

```shell
git checkout -b <new_branch>
git checkout -b <new_branch> <remote_rep>/<remote_branch> # 创建一个新分支并且跟踪远程仓库中的分支
```

比如

```shell
git remote add upstream <url>
git checkout -b new_feature upstream/master
```

本地分支跟踪远程分支

```shell
# 查看跟踪情况
git branch -vv
# 创建一个新分支并且跟踪远程仓库中的分支
git checkout -b <new_branch> <remote_rep>/<remote_branch> 
# 为本地分支设置一个远程跟踪分支
git branch --set-upstram-to=<remote_rep>/<remote_branch> 
```

拉取远程分支的信息与推送

```shell
# 拉取 origin 仓库的 master 分支并合并数据到当前分支
git pull origin master 

# 拉取并且重置本地分支，本地的修改会丢弃，和远程分支完全同步
git fetch origin
git reset --hard origin/<branch_name>

# 推送数据到远程仓库分支
git push origin <branch_name>
git push origin <tag-name> # 推送标签

# 安全的强制推送，强制推送并检查是否会覆盖远程仓库中的内容，如果本地落后于远处，将拒绝推送
git push --force-with-lease origin master
```

暂时保存当前修改的方法。
`git stash`默认只会保存已跟踪的文件。
查看`stash`

```shell
git stash list
```

删除`stash`

```shell
git stash drop stash@{0} # 删除某个 stash
git stash clear # 删除所有的 stash
git stash pop # 应用并删除 stash
git stash apply # 应用最近的 stash，且不删除
git stash apply stash@{1} # 应用某个 stash, 且不删除
```

临时切换分支

```shell
git stash # 保存已暂存和当前工作区的修改
git checkout <other_branch> # 切换到目标分支
git checkout <last_branch> # 完成工作后返回原来的分支
git stash pop # 恢复之前的修改
```

避免冲突，在拉取远程数据合并到本地之前，可能会有冲突，可以先保存本地的修改

```shell
git stash # 暂存修改
git pull origin master # 拉取远程更改
git stash pop # 恢复本地修改
```

删除分支

```shell
git branch -d <branch_name>
git branch -D <branch_name> # 强制删除未合并的分支
git push origin --delete <branch_name> # 删除 origin 仓库中的远程分支
```

合并分支

```shell
git checkout master # 切换回 master
git merge hot_fix # 在 master 上合并来自 hot_fix 的修改
```

合并冲突的解决

合并如果产生冲突，需要我们手动解决。在 `======` 以上的部分是 `HEAD` 版本的内容

变基

`git rebase`会将一个分支的更改“复制”到另一个分支的顶部，实际上是重写历史，将目标分支的历史变基到当前分支之后。与合并不同，变基不会生成额外的合并提交。

`git rebase` 会让 `feature` 分支的提交看起来像是直接在 `master` 分支上继续开发的，没有合并提交

```shell
# 切换到功能分支，并执行变基操作
git checkout <feature_branch>
git rebase master

# 如果产生冲突
git add <resolved_files>
git rebase --continue
```

只对自己本地尚未推送的更改进行**变基**操作

## 其他不常用的命令




