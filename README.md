# 星穹铁道自动对话工具

一个简单的崩坏：星穹铁道自动对话工具，可以自动检测剧情对话并点击继续。使用到opencv所以把原来的c重构成了py。代码参考[SyrieYume/GenshinAutoV2: 原神后台自动点剧情工具 v2版本。](https://github.com/SyrieYume/GenshinAutoV2)

## 系统要求

- Windows操作系统
- 游戏需要以窗口模式运行，目前仅支持1920×1080分辨率

## 使用方法

### 直接使用预编译版本

1. 在[Releases](https://github.com/ywq1145/StaRailAutoSkipV2/releases)下载最新的发布版本 
2. 运行游戏，确保是窗口模式
3. 运行 `autoDialog.exe`。
4. 程序会自动检测游戏窗口并开始监控剧情对话（通过检测像素，所以别开滤镜），此时游戏可切至后台
5. 按 `Ctrl+P` 可以随时暂停/继续自动点击功能

### 从源代码编译

如果你想自己修改与打包项目，需要安装python和requirements中的包。

打包命令：

```bash
pyinstaller package.spec --noconfirm --clean --distpath ./dist --workpath ./build
```
使用nuitka使用pack_nuitka.txt的命令（似乎用这个打包不能用conda）。

## 工作原理

程序通过以下步骤实现自动点击功能：

1. 检测 StarRail.exe 进程并获取窗口句柄
3. 对游戏窗口进行截图，并当检测到剧情对话界面特征时，自动向游戏窗口发送按键消息（当检测到箭头也就是一些必选项后往左截图，匹配此选项对应的数字并发送，没箭头时点空格和1）。
4. 发送按键

