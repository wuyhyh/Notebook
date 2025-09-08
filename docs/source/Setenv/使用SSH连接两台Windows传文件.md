# 使用 SSH 连接两台 Windows 传文件



## Appendix. 恢复 Windows 11 邮件显示完整菜单

编辑保存 `right_click_config.bat` 文件

```text
@echo off
reg add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /ve /d "" /f
taskkill /f /im explorer.exe & start explorer.exe
echo Windows 11 右键菜单已恢复完整选项！
pause
```

右键以管理员身份运行

