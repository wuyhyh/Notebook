# oebuild 构建可能出现的问题

## 5.3 可能的编译问题

### 5.3 可能的编译问题

#### 5.3.1 编译 binutils 出现 gold 链接问题

这版 binutils 把 dwp 放在 gold 目录下。某些组合下它会被错误地用 ld.bfd 去链接并把 libgold.a 拉进来，但缺少 gold
需要的其它对象/顺序/配置，导致这些 gold:: 符号解析失败。常见修法是禁用 gold（连带 dwp），或者让目标侧 libstdc++ 等在那一步可用；

```text
cd ~/openeuler/workdir/src/yocto-meta-openeuler/meta-openeuler/recipes-devtools/binutils
```

修改 binutils_%.bbappend 内容：

```text
# 关闭 gold（同时就不会去构建 gold 目录下的 dwp）
PACKAGECONFIG:remove = " gold"
EXTRA_OECONF:append = " --disable-gold"
```

因为是增量编译的，可以回到工作目录继续重新编译

```text
cd ~/openeuler/workdir/build/phytium
oebuild bitbake -c cleansstate binutils
oebuild bitbake openeuler-image
```

#### 5.3.2 openssl

稳定构建 `openssl`/`openssl-native`，避免 `do_compile`/`do_install` 并行导致的竞态与 fuzz/test 目标引发的链接异常。

##### 一、在 `local.conf` 增加配置（最快）

编辑 `build/conf/local.conf`，追加如下行：

```text
# 1) 禁用并行编译与并行安装（openssl 及其 native 变体）
PARALLEL_MAKE:pn-openssl = ""
PARALLEL_MAKEINST:pn-openssl = ""
PARALLEL_MAKE:pn-openssl-native = ""
PARALLEL_MAKEINST:pn-openssl-native = ""

# 2) 关闭测试与 fuzz 相关目标（生产环境不需要，减少不确定性）
EXTRA_OECONF:append:pn-openssl = " no-tests no-fuzz-afl no-fuzz-libfuzzer"
EXTRA_OECONF:append:pn-openssl-native = " no-tests no-fuzz-afl no-fuzz-libfuzzer"
```

##### 二、清理并重建

```bash
# 进入你的 oebuild 工作目录
cd <work>

# 清理旧产物（避免复用到已损坏/不完整的缓存）
bitbake -c cleansstate openssl-native openssl

# 先单包验证，再继续整体构建
bitbake openssl-native
bitbake openssl

# 通过后继续你的镜像/目标
bitbake <your-image-or-target>
```

##### 三、可选：长期化（更规范，用 bbappend）

如果希望把规避策略沉淀到自定义层，创建：

```
meta-local/recipes-connectivity/openssl/openssl_%.bbappend
```

内容：

```text
PARALLEL_MAKE = ""
PARALLEL_MAKEINST = ""
EXTRA_OECONF:append = " no-tests no-fuzz-afl no-fuzz-libfuzzer"
```

把 `meta-local` 加入 `bblayers.conf` 后，执行同样的清理与重建步骤。

##### 四、验证要点

* 构建日志不再出现 `mv: cannot stat ...*.d.tmp`、`libcrypto.a: malformed archive`、`OPENSSL_die` 未解析等并行/竞态类错误。
* `tmp/work/.../openssl-*/image/` 下文件完整；镜像里 `openssl`/`libssl`/`libcrypto` 安装正常。

#### 5.3.3 dtc 时间戳问题

```text
source ~/venvs/oebuild/bin/activate
oebuild bitbake -c cleansstate dtc-native
oebuild bitbake dtc-native
```

#### 5.3.4 内核编译缺少依赖

##### 问题现象

* `linux-openeuler-5.10-r0 do_compile: oe_runmake failed`
* 随后在尝试补依赖时又出现：

    * `Nothing PROVIDES 'dwarves-native'`（应为 `pahole-native`）
    * `Nothing PROVIDES 'libelf-native'`（应为 `elfutils-native`）

##### 根因

1. Yocto 内核开启了 BTF（`CONFIG_DEBUG_INFO_BTF=y`），内核链接 `BTF` 需要 `pahole` 与 `libelf` 等原生工具。
2. 我们在 `local.conf` 里用错了依赖名称：

    * `dwarves-native` → 实际配方名是 `pahole-native`
    * `libelf-native` → 实际配方名是 `elfutils-native`
3. 因 provider 名称不匹配，BitBake 无法解析依赖，导致目标 `linux-openeuler` “no buildable providers”。

##### 解决方案

1. 在 `build/conf/local.conf` 正确补齐原生依赖：

```text
# 给 linux-openeuler 补齐原生依赖
DEPENDS:append:pn-linux-openeuler = " dtc-native bc-native openssl-native elfutils-native pahole-native flex-native bison-native"
```

2. 清理并重建：

```text
oebuild bitbake -c cleansstate linux-openeuler elfutils-native pahole-native
oebuild bitbake linux-openeuler
```

这套配置能稳定把 `linux-openeuler` 编过去；后续若开启更多内核特性（模块签名、LTO 等）再逐项补齐依赖或加碎片即可。





