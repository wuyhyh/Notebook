# 使用串口工具更新 U-Boot

当 U-Boot 没有实现网络功能时，我们可以通过串口传输新版的 U-Boot对其进行更新。

<a href="../_static/files/fip-all.bin" download="fip-all.bin" class="btn btn-primary">下载 fip-all.bin</a>
<button class="btn sha-btn" onclick="copySha(this)"> 
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
       stroke-linecap="round" stroke-linejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2"></rect>
    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
  </svg>
  <span>SHA256</span>
</button>

<script>
async function copySha(el) {
  const old = el.innerHTML;
  const txt = await fetch('../_static/files/fip-all.bin.sha256').then(r=>r.text());
  const sha = (txt.match(/[0-9a-fA-F]{64}/)||[''])[0];
  if (!sha) return;
  try {
    await navigator.clipboard.writeText(sha);
  } catch {
    const ta=document.createElement('textarea');
    ta.value=sha;document.body.appendChild(ta);ta.select();
    document.execCommand('copy');document.body.removeChild(ta);
  }
  el.innerHTML='✅ 已复制'; setTimeout(()=>{el.innerHTML=old;},1200);
}
</script>

串口传 fip-all.bin → 写入 Flash → 校验 → 重启的流程：
Tera Term 发送 YMODEM；MobaXterm（串口终端）；U-Boot 端用 `loady`（YMODEM）；写 Flash 用板子里已有的 `flashw` 命令

## 1. 用 Tera Term 发送 YMODEM

**MobaXterm 的串口会话没有内置 X/Y/ZMODEM 的“Transfer/传输”菜单**，所以先使用 Tera Term传输文件。

### 1.1 设置波特率

安装并打开 Tera Term → 选 **Serial**，选择你的 COM 口，波特率和 U-Boot 一致 （如 **115200** 8N1）。

### 1.2 等待开始传输

在 U-Boot 命令行

```
setenv loadaddr 0x90000000
loady $loadaddr
```

出现 “Ready for binary (ymodem)” 提示后停住等待。

### 1.3 选择文件开始传输

> 传输之前要设置 Tera Term 的波特率为 115200，关闭 VPN

在 Tera Term：**File → Transfer → YMODEM → Send...**，选中 `fip-all.bin`，等进度条走完。

> `filesize` 是十六进制；擦写 Flash 前要把擦除大小按扇区（常见 64KB）对齐。



现在 `fip-all.bin` 文件已经下载到了内存地址 0x90000000 处

## 2. 切换到 MobaXterm 擦写 flash 芯片

MobaXterm 比 Tera Term 对视觉友好多了，传输完文件我们可以换回这个工具继续使用。

传完后 U-Boot 会将传输字节数写入环境变量 `filesize`（16 进制）。你可查看：

```text
echo $filesize
```

> 可选校验，记下 CRC 以便之后比对。
>
> ```text
> crc32 $loadaddr $filesize
> ```
>

write 之前先进行 erase

```text
flashe <start_addr> <end_addr>
flashw <loadaddr> <start_addr> $filesize
```

## 3. 重启验证

写完并校验通过后，下电系统，然后上电重新启动
