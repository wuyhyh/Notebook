# 初始化 earlycon

设备树这块可以概括成两条改动：

---

## 1. 在 SoC 公共 dtsi 里补齐 UART 的 alias

文件：`pd2008-generic-psci-soc.dtsi`

在原来的：

```text
aliases {
    ethernet0 = &gmac0;
    ethernet1 = &gmac1;
};
```

基础上增加串口别名，让 `stdout-path = "uart1:115200n8"` 真正能找到节点：

```text
aliases {
    ethernet0 = &gmac0;
    ethernet1 = &gmac1;

    /* 新增：给 earlycon / stdout-path 用的串口别名 */
    serial0 = &uart1;
    uart1   = &uart1;
};
```

这样内核解析 `/chosen/stdout-path` 时，`uart1` 和 `serial0` 都是有效的 alias，earlycon 不会再报 “stdout-path uart1 not found”。

---

## 2. 在板级 dts 中可选地规范 stdout-path

文件：`pd2008-devboard-dsk.dts`

原来类似：

```text
/ {
    chosen {
        stdout-path = "uart1:115200n8";
    };
    ...
};
```

可以保持不动，或者改成更常见的写法（可选）：

```text
/ {
    chosen {
        stdout-path = "serial0:115200n8";
    };
    ...
};
```

因为上一步已经把 `serial0` 指向 `&uart1`，实际用的还是同一个 UART，只是名字更规范。

---

做到这两步后：

* 继续在 `bootargs` 里写裸的 `earlycon` 也可以顺利初始化 earlycon；
* 内核不会再打印 `OF: fdt: earlycon: stdout-path uart1 not found`。
