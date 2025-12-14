# 软件设计

一些需要优化的软件设计。

## 1. NVMe over PCIe

NVMe SSD和PCIe总线的关系可以这样看：

1. **接口层面：NVMe是跑在PCIe上的协议**

    * PCIe是总线/传输通道，负责“怎么把数据高速送过去”；
    * NVMe是存储协议，负责“怎么和SSD里的控制器说话”。
    * 所以NVMe≠PCIe，它是“NVMe over PCIe”。

2. **硬件拓扑：NVMe SSD本质上就是一块挂在PCIe上的设备**

    * NVMe盘在主机眼里就是一个PCIe Endpoint，像网卡、显卡一样挂在某条PCIe通道上；
    * 主板/SoC上要么有直出的PCIe Root Port，要么通过PCIe交换芯片再连到NVMe。

3. **性能的关键点在PCIe带宽**

    * NVMe能快，是因为直接用PCIe的多lane、高带宽、低延迟；
    * 一条PCIe Gen3 x4的理论带宽大约4 GB/s量级，Gen4 x4可到7 GB/s左右，Gen5 x4更高；
    * 你如果把NVMe挂在x2、Gen3之类的窄/旧链路上，性能就被PCIe瓶颈卡住。

4. **协议分工：为什么不是SATA/AHCI**

    * 传统SATA走的是AHCI协议，为旋转盘设计，队列深度小、锁多；
    * NVMe专门为PCIe直连的闪存设计，多队列、每队列深，延迟低；
    * 也有“SATA SSD”这种盘，但那是走SATA总线，不走PCIe，也就不是NVMe。

5. **软件视角（操作系统里）**

    * OS先枚举到一个PCIe设备 → 发现它是NVMe类设备 → 用nvme驱动和它说NVMe协议 → 暴露成块设备 `/dev/nvme0n1`；
    * 所以你能看到“PCIe能看到设备，但Linux里没有nvme块设备”这种问题，多半是链路有了但NVMe枚举/驱动没走通。

6. **特殊情况**

    * 有的SoC里是“PCIe控制器 + NVMe控制器”更紧耦合，看起来像直接支持NVMe，其实底层还是走PCIe思想；
    * U.2、M.2、E1.S这些更多是“物理形态/连接方式”，真正的数据还是NVMe over PCIe。

一句话收尾：**NVMe SSD是挂在PCIe上的存储设备，PCIe给通道，NVMe给说话方式；没有PCIe（或等价的传输），NVMe就没处跑。**

## 2. U-Boot 放在 spi nor flash 还是 nvme ssd 中

下面把两种放置方式拆开对比，并给出各自典型场景与推荐组合。

### 核心结论

* **内核/设备树放 NVMe**：容量充足、更新灵活，适合服务器/存储设备、桌面级或需要频繁更新的大系统。但**依赖 U-Boot 侧 PCIe/NVMe
  就绪**，启动链复杂度更高。
* **内核/设备树放 NOR Flash**：启动依赖小、确定性强、容错好，适合工业/网络设备、车规、无人值守现场等对可靠性与可预期启动时间敏感的场景。容量受限，更新策略需要设计（双镜像/救援）。

### 维度对比

| 维度         | 放在 NVMe                                     | 放在 NOR Flash                         |
|------------|---------------------------------------------|--------------------------------------|
| 启动依赖       | 需要 U-Boot 初始化 PCIe、枚举 NVMe、U-Boot NVMe 驱动可用 | 仅需 SPI 控制器即可，依赖少                     |
| 启动耗时       | 多一步 PCIe 链路训练+设备枚举，冷启动略慢                    | 更快、更确定                               |
| 容量         | 充裕，可放大型内核+大 initramfs                       | 受限（常见 16–128 MB 级别），不适合很大的 initramfs |
| 更新与回滚      | 在 NVMe 上做 A/B 分区、OSTree/RAUC/SWUpdate 较容易   | 需要双 Bank/双镜像或外部介质升级，NOR 擦写慢          |
| 可靠性/容错     | 需考虑 NVMe 盘/文件系统损坏；要有 fallback               | 天然更稳，可以只读保护，抗电掉电好                    |
| 硬件成本/功耗    | 盘本身成本与功耗更高                                  | 控制器+小容量 NOR 成本/功耗低                   |
| 安全链（签名/验证） | 可在 U-Boot 验证 FIT/签名后再从 NVMe 读               | 可把签名的 FIT 直接放 NOR，链路短、容易封闭           |
| 适配复杂度      | U-Boot 侧需完善 PCIe/NVMe 驱动与脚本                 | 简单，板级适配工作量小                          |

### 典型适用场景

#### 适合把内核/设备树放 **NVMe** 的场景

* **服务器/边缘存储/桌面级 SoC**：内核与根文件系统都大、更新频繁，需要包管理/容器等重负载生态。
* **需要 A/B 滚动升级**：在 NVMe 上做 `boot(A/B) + rootfs(A/B) + data`，升级/回滚快且可在线。
* **需要很大的 initramfs 或多套内核**：NOR 放不下时自然落到 NVMe。

注意：这要求**U-Boot 阶段**能稳定把 PCIe/NVMe 拉起来（你板上的 U-Boot + 控制器驱动要成熟），否则现场风险高。

#### 适合把内核/设备树放 **NOR Flash** 的场景

* **工业控制、网络设备（路由器、交换机、网关）、车规/轨道等**：强调上电即起、确定性与容错，一般把引导链尽量短。
* **无人值守**：可把 NOR 设为只读，避免误操作/掉电损坏；需要升级时用双镜像/救援分区。
* **板卡资源有限、无 PCIe 或 NVMe 驱动成熟度存疑**：避免把“能不能起”绑在复杂外设上。

### 工程上常用的三种组合

1. **保守可靠型（强烈推荐在你现在的阶段）**

    * **NOR**：SPL/TF-A/U-Boot + 一套“救援”内核/DTB/小 initramfs（只要能进系统、修盘/回滚即可）。
    * **NVMe**：正常运行的 `boot + rootfs(A/B) + data`。
    * **策略**：U-Boot 先尝试 NVMe 正常路 → 失败若干次（`bootcount/bootlimit`）自动切回 NOR 的救援镜像。
    * 优点：生产可用的稳健架构；NVMe 不可用时仍能维修。

2. **性能/开发灵活型**

    * **NOR**：只放 TF-A/U-Boot。
    * **NVMe**：放内核/DTB/initramfs 与 rootfs。
    * **策略**：U-Boot 直接从 NVMe 读取并 `booti`。
    * 适合实验室、开发阶段或对可靠性要求不那幺苛刻的设备。

3. **极简可靠型**

    * **NOR**：放 TF-A/U-Boot + 生产内核/DTB + 小根（initramfs）。
    * **NVMe**：只做数据或二级组件（可选）。
    * 适合没有 PCIe 的平台，或强约束设备。

### 你在 D2000 板卡上的注意事项与建议

* **建议优先采用“保守可靠型”**：把可引导的救援内核/DTB+小 initramfs 固化在 NOR；把正式内核/DTB 与 rootfs 放 NVMe。
* **U-Boot 环境策略**：

    * 开启 `bootcount/bootlimit`，失败 N 次自动走 `altbootcmd`（救援路径）。
    * `boot_targets` 先 `nvme`，再 `nor_rescue`。
* **内核配置**：若“内核在 NOR、rootfs 在 NVMe”，请将 **PCIe/NVMe 驱动编译为 built-in（=y）**，确保内核起步即能挂载 NVMe
  根；或把所需模块打进 initramfs。
* **分区建议（NVMe）**：

    * `p1: /boot`（ext4 或 FAT32，存放 Image/DTB/initramfs/extlinux.conf 或 FIT）
    * `p2: rootfsA`，`p3: rootfsB`
    * `p4: data`
* **文件完整性与签名**：推荐用 **FIT**（带哈希/签名），U-Boot 验证后再启动，来源可为 NOR 或 NVMe。
* **掉电/损坏恢复**：救援 initramfs 中准备 `nvme-cli`、`e2fsck`、`dd`、升级脚本，便于远程/现场维护。

#### 参考启动脚本思路（示意）

```sh
# 正常路径：NVMe
setenv try_nvme 'nvme scan; ext4load nvme 0:1 ${kernel_addr_r} /boot/Image &&
                 ext4load nvme 0:1 ${fdt_addr_r} /boot/board.dtb &&
                 booti ${kernel_addr_r} - ${fdt_addr_r}'

# 失败回退：NOR 救援（示意，按你板子的 sf 命令/偏移调整）
setenv rescue 'run load_nor_kernel && run load_nor_fdt && booti ${kernel_addr_r} - ${fdt_addr_r}'

setenv bootlimit 3
setenv bootcmd 'if run try_nvme; then; else run rescue; fi'
saveenv
```

### 选择建议（快速决策）

* **重可靠、强确定性、长寿命设备** → 内核/DTB 放 **NOR**，NVMe 做运行盘或数据，保留救援路径。
* **容量大、更新频繁、快速迭代** → 内核/DTB 放 **NVMe**，但务必设计 **NOR 救援** 与 **A/B 回滚**。
* **研发生产并行** → 开发期放 NVMe、量产改为 NOR+救援 的混合架构，统一脚本和验证链，减少切换成本。

## 3. 多核处理器混合部署OS

软硬件形态是什么样的？

共享内存不止局限在进程通信中，那么两个系统如何共享内存？

内核裁剪到 400 MB 是非常困难的，但是可能吗？

启动时间 5 s

实时和非实时系统会不会竞争资源？



