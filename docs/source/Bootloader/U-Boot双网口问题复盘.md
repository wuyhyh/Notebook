# U-Boot 双网口问题复盘报告（D2000 + 8211 PHY）

PHY 并不总“依赖软件”去调用重启协商；是否需要取决于上电默认与驱动流程。
但在很多厂商分支/裁剪后的 U-Boot 里，稳妥做法是：在每个实际要用的端口上，完成配置后显式 genphy_restart_aneg() 一次。

## 1. 背景

* 平台：Phytium D2000，U-Boot 2019.07 厂商分支
* 现象：

    * 按“厂商新版 Linux 设备树 + U-Boot 旧版设备树”的建议接入网口。
    * 板级新增 PHY 私有配置，仅**面向 MAC0（eth0）**。
    * 启动后 **eth0 可用**，**eth1 链路 up 但 ping 不通**（ARP 超时）。
* 目标：在不破坏 eth1 的前提下，对 MAC0 的 PHY 下发定制寄存器序列，使两口均可正常通信。

---

## 2. 事件时间线（要点）

1. 增加 `board_phy_config()`，对 MAC0 下的 8211 执行寄存器序列；eth1 异常。
2. 观察到 `board_phy_config()` 对每个 PHY 都会被调用；怀疑误命中或副作用。
3. 尝试 `misc_init_r()` + fixup 方案，但厂商树缺少 `phy_register_fixup_for_uid()`。
4. 回退到 `board_phy_config()`；改为“仅命中 MAC0”的判定（不依赖节点路径），问题仍在。
5. 发现 eth1 未执行自协商；对非 MAC0 明确调用 `genphy_restart_aneg()` 后，**eth1 恢复**。
6. 收敛实现，确保每口仅触发一次自协商，eth0/eth1 均工作稳定。

---

## 3. 复现与诊断要点

* `mii device` 可见两条 MDIO：`ethernet0@2820c000`、`ethernet1@28210000`。
* 两路 PHY **地址均为 0x7**，无法用地址区分；UID 读取异常（ID1=0x0000），推断为历史写页未恢复或驱动裁剪。
* `ping` eth1 时出现 `ARP Retry count exceeded`；同时 `link=1, 1000/full duplex` → 多为“未协商/协商未生效/收发错码”而非物理链路问题。
* 临时将非 MAC0 路径中补上 `genphy_restart_aneg()`，问题消失。

---

## 4. 根因分析

1. **初始化时序/职责划分问题**

    * 厂商树将“触发自协商”的职责放在板级钩子 `board_phy_config()` 中。
    * 覆盖该钩子后，非 MAC0（eth1）路径**没有人再触发自协商**，导致虽有 link，但 ARP 不通。
2. **辅助因素**

    * 两口 PHY 地址相同（0x7），不能以地址过滤，只能以“MDIO 父设备=MAC 实例”区分。
    * 早期私有序列可能修改过页选择/扩展寄存器，若不恢复，会造成后续读 ID 异常并干扰诊断。
    * 交换机侧 MAC/ARP 学习与 `ethaddr/eth1addr` 未区分可能放大现象（已通过区分 MAC 与清表规避）。

---

## 5. 变更内容（最终实现）

在板级文件中覆盖弱符号 `board_phy_config()`，策略：

* **仅在 MAC0** 执行私有寄存器序列；
* **非 MAC0** 不修改寄存器，但**显式触发一次自协商**；
* 两条路径都确保“每口仅触发一次”，并**始终返回 0**，不阻断默认流程。

在板级初始化代码中增加初始化 PHY 芯片寄存器的命令

```text
board/phytium/D2000/d2000.c
```

示例（核心逻辑）：

```c++
/* 覆盖弱符号：仅在 MAC0 的 PHY 上生效；不看 UID、不看地址 */
int board_phy_config(struct phy_device *phydev)
{
        /* 真命中才执行 PHY 寄存器配置序列；成功后重启自协商使配置生效 */
        if (is_phydev_belongs_to_mac0(phydev)) {
                if (!chip_8211_phy_seq(phydev))
                        genphy_restart_aneg(phydev);
                return 0;
        }

        /* 不是 MAC0：直接自协商 */
        genphy_restart_aneg(phydev);
        return 0;
}
```

配套注意：

* `chip_8211_phy_seq()` 内部对页选择/扩展 MMD访问需 **保存并恢复**；结束后不留“全局页”副作用。
* `.config` 打开 `CONFIG_DM_ETH`、`CONFIG_PHYLIB` 及对应 PHY 驱动。
* U-Boot 环境中为两口设置不同 MAC：`ethaddr` 与 `eth1addr`。
* 避免 `ipaddr == serverip` 的自测假阳性。

---

## 6. 效果验证

* `eth0`：`ping` 服务器成功，速率/双工正确；
* `eth1`：`genphy_update_link` 显示 up，`ping` 正常；ARP 不再超时。
* 多次冷启动/热复位复测，行为稳定。

---

## 7. 结论

问题并非驱动缺陷，而是**初始化职责被板级覆盖后遗漏了对第二口的自协商触发**。通过在 `board_phy_config()` 中：

* 对 **MAC0** 执行私有序列 + 重启协商；
* 对 **非 MAC0** 明确补一次重启协商；
  恢复了两口网络的正常工作，且实现简单、时序安全、可维护性好。
