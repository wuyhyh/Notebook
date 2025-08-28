# 使用串口工具更新 U-Boot

当 U-Boot 没有实现网络功能时，我们可以通过串口传输新版的 U-Boot对其进行更新。

串口传 fip-all.bin → 写入 Flash → 校验 → 重启的流程：
Tera Term 发送 YMODEM；MobaXterm（串口终端）；U-Boot 端用 `loady`（YMODEM）；写 Flash 用板子里已有的 `flashw` 命令

## 1. 用 Tera Term 发送 YMODEM

**MobaXterm 的串口会话没有内置 X/Y/ZMODEM 的“Transfer/传输”菜单**，所以先使用 Tera Term传输文件。

1. 安装并打开 Tera Term → 选 **Serial**，选择你的 COM 口，波特率和 U-Boot 一致（如 115200 8N1）。

2. 确定 RAM 地址可用：你打算放到 `0x90000000`，一般在 DDR 的安全范围内。可快速探测：

   ```
   md.b 0x90000000 10
   mw.b 0x90000000 00 100
   ```
3. 在 U-Boot：

   ```
   setenv loadaddr 0x90000000
   loady $loadaddr
   ```

   出现 “Ready for binary (ymodem)” 提示后停住等待。
4. 在 Tera Term：**File → Transfer → YMODEM → Send...**，选中 `fip-all.bin`，等进度条走完。

> • `filesize` 是十六进制；擦写 Flash 前要把擦除大小按扇区（常见 64KB）对齐。

现在 `fip-all.bin` 文件已经下载到了内存地址 0x90000000 处

## 2. 切换到 MobaXterm

MobaXterm 比 Tera Term 对视觉友好多了，传输完文件我们可以换回这个工具继续使用。

1. 串口连接：115200 8N1，流控 None。进入 U-Boot 提示符（`=>`）。

2. 在 MobaXterm 串口窗口：菜单栏点 `Transfer` → `YMODEM` → `Send...`，选中你的 `fip-all.bin`。
   传完后 U-Boot 会显示传输字节数，并把大小写入环境变量 `filesize`（16 进制）。你可查看：

   ```
   echo $filesize
   ```

   > 可选校验（建议）：
   >
   > ```
   > crc32 $loadaddr $filesize
   > ```
   >
   > 记下 CRC 以便之后比对。

## 3. 用 `flashw` 写入

先看语法：

```
help flashw
```

write 之前先进行 erase

```text
flashe start_addr end_addr
flashw loadaddr start_addr $filesize
```

## 4. 重启验证

写完并校验通过后：

```
reset
```

让前级 BootROM/BL1 按既定偏移加载 FIP 启动。
