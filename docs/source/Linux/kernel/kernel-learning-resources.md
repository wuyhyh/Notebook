# Kernel Learning Resources (Modern & Practical)

> Notes
>
> - 本清单来自内核文档中的 *Index of Further Kernel Documentation* 相关内容整理。
> - 同一小节内资源按“新 → 旧”排序。
> - 除“基础经典书”外，其它资源应定期淘汰过时条目。

---

## 1. Kernel Tree 内置文档（首选）

### 1.1 Linux kernel 源码自带 Documentation/

- **Name**: linux/Documentation
- **Author**: Many
- **Location**: `Documentation/`
- **Keywords**: text files, Sphinx
- **Description**: 随内核源码维护的官方文档目录；部分页面可能比 web 版本更新。
- **Build**: `make htmldocs` / `make pdfdocs` / `make epubdocs`

> 知道 `Documentation` 目录的存在性和重要性就行了，在有网络的情况下网页版更方便，阅读体验更好。

- 最新版: https://docs.kernel.org/index.html
- 5.10 内核: https://www.kernel.org/doc/html/v5.10/
- 5.10 内核关于 PCI 的部分: https://www.kernel.org/doc/html/v5.10/PCI/pci.html

---

## 2. 在线文档（Online docs）

### 2.1 Linux Kernel Mailing List Glossary（术语表）

- **Title**: Linux Kernel Mailing List Glossary
- **Author**: various
- **URL**: https://kernelnewbies.org/KernelGlossary
- **Date**: rolling
- **Keywords**: glossary, terms, linux-kernel
- **Description**: LKML 常见缩写与术语速查。

### 2.2 The Linux Kernel Module Programming Guide（LKMPG）

- **Title**: The Linux Kernel Module Programming Guide
- **Author**: Peter Jay Salzman, Michael Burian, Ori Pomerantz, Bob Mottram, Jim Huang
- **URL**: https://sysprog21.github.io/lkmpg/
- **Date**: 2021
- **Keywords**: modules, GPL book, /proc, ioctls, system calls, interrupt handlers
- **Description**: 内核模块编程 GPL 书，示例较多；新版本维护在：
    - Repo: https://github.com/sysprog21/lkmpg

---

## 3. 已出版书籍（Published books）

### 3.1 The Linux Memory Manager

- **Title**: The Linux Memory Manager
- **Author**: Lorenzo Stoakes
- **Publisher**: No Starch Press
- **Date**: February 2025
- **Pages**: 1300
- **ISBN**: 978-1718504462
- **Notes**: 内存管理；early access draft 可预购获取；正式版计划 2026 Fall：
    - https://nostarch.com/linux-memory-manager

### 3.2 Practical Linux System Administration (1st Edition)

- **Title**: Practical Linux System Administration: A Guide to Installation, Configuration, and Management
- **Author**: Kenneth Hess
- **Publisher**: O’Reilly Media
- **Date**: May 2023
- **Pages**: 246
- **ISBN**: 978-1098109035
- **Notes**: 系统管理方向。

### 3.3 Linux Kernel Debugging

- **Title**: Linux Kernel Debugging: Leverage proven tools and advanced techniques to effectively debug Linux kernels
  and kernel modules
- **Author**: Kaiwan N Billimoria
- **Publisher**: Packt Publishing Ltd
- **Date**: August 2022
- **Pages**: 638
- **ISBN**: 978-1801075039
- **Notes**: 内核与模块调试。

### 3.4 Linux Kernel Programming

- **Title**: Linux Kernel Programming: A Comprehensive Guide to Kernel Internals, Writing Kernel Modules, and Kernel
  Synchronization
- **Author**: Kaiwan N Billimoria
- **Publisher**: Packt Publishing Ltd
- **Date**: March 2021（Second Edition: 2024）
- **Pages**: 754
- **ISBN**: 978-1789953435（Second Edition: 978-1803232225）
- **Notes**: 内核内部机制 + 模块 + 同步。

### 3.5 Linux Kernel Programming Part 2

- **Title**: Linux Kernel Programming Part 2 - Char Device Drivers and Kernel Synchronization
- **Author**: Kaiwan N Billimoria
- **Publisher**: Packt Publishing Ltd
- **Date**: March 2021
- **Pages**: 452
- **ISBN**: 978-1801079518
- **Notes**: 字符设备驱动 + 用户/内核接口 + 中断与同步。

### 3.6 Linux System Programming（基础书）

- **Title**: Linux System Programming: Talking Directly to the Kernel and C Library
- **Author**: Robert Love
- **Publisher**: O’Reilly Media
- **Date**: June 2013
- **Pages**: 456
- **ISBN**: 978-1449339531
- **Notes**: Foundational book（偏系统编程，非内核实现）。

### 3.7 Linux Kernel Development, 3rd Edition（基础书）

- **Title**: Linux Kernel Development (3rd Edition)
- **Author**: Robert Love
- **Publisher**: Addison-Wesley
- **Date**: July 2010
- **Pages**: 440
- **ISBN**: 978-0672329463
- **Notes**: Foundational book。

### 3.8 Linux Device Drivers, 3rd Edition（基础书）

- **Title**: Linux Device Drivers (3rd Edition)
- **Author**: Jonathan Corbet, Alessandro Rubini, Greg Kroah-Hartman
- **Publisher**: O’Reilly & Associates
- **Date**: 2005
- **Pages**: 636
- **ISBN**: 0-596-00590-3
- **Notes**: Foundational book；LWN 上的 PDF 入口：
    - https://lwn.net/Kernel/LDD3/

### 3.9 The Design of the UNIX Operating System（基础书）

- **Title**: The Design of the UNIX Operating System
- **Author**: Maurice J. Bach
- **Publisher**: Prentice Hall
- **Date**: 1986
- **Pages**: 471
- **ISBN**: 0-13-201757-1
- **Notes**: Foundational book（经典 UNIX 设计，偏理念/结构）。

---

## 4. 杂项工具与站点（Miscellaneous）

### 4.1 Cross-Referencing Linux（源码交叉引用浏览）

- **Name**: Cross-Referencing Linux
- **URL**: https://elixir.bootlin.com/
- **Keywords**: Browsing source code
- **Description**: Web 版内核源码浏览器，函数/变量定义与引用交叉链接非常好用。

### 4.2 Linux Weekly News（LWN）

- **Name**: Linux Weekly News
- **URL**: https://lwn.net
- **Keywords**: latest kernel news
- **Description**: 每周内核工作与版本/特性汇总，适合跟进演进与社区讨论。

### 4.3 Linux-MM（内存管理开发站点）

- **Name**: The home page of Linux-MM
- **Author**: The Linux-MM team
- **URL**: https://linux-mm.org/
- **Keywords**: memory management, Linux-MM, mm patches, TODO, docs, mailing list
- **Description**: 内存管理方向的补丁、TODO、文档与开发者信息聚合站。

---

## 5. 社区与交流（Community）

### 5.1 Kernel Newbies IRC & Website

- **Name**: Kernel Newbies IRC Channel and Website
- **URL**: https://www.kernelnewbies.org
- **Keywords**: IRC, newbies, channel, asking doubts
- **Description**:
    - IRC: `#kernelnewbies` on OFTC (`irc.oftc.net`)
    - 网站也托管文章/FAQ/入门文档。

---

## 6. 邮件列表归档与检索（Mailing list archives & search）

### 6.1 Subspace

- **Name**: linux-kernel mailing list archives and search engines
- **URL**: https://subspace.kernel.org
- **Keywords**: linux-kernel, archives, search

### 6.2 lore.kernel.org

- **Name**: linux-kernel mailing list archives and search engines
- **URL**: https://lore.kernel.org
- **Keywords**: linux-kernel, archives, search
- **Description**: LKML 等邮件列表的归档与检索入口。

---

## 7. 视频与会议（Videos & Conferences）

### 7.1 The Linux Foundation YouTube channel

- **Name**: The Linux Foundation YouTube channel
- **URL**: https://www.youtube.com/user/thelinuxfoundation
- **Keywords**: linux, videos, linux-foundation, youtube
- **Description**: Linux Foundation 相关会议与活动录像、技术内容合集。
