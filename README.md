# 星穹铁道自动对话工具

## 安装与使用

1. 从[Releases](https://github.com/yourusername/StarRailAuto/releases)页面下载最新版本的`星穹铁道自动对话.exe`
2. 双击运行，会自动请求管理员权限
3. 程序会自动等待星穹铁道游戏启动

## 工作原理

该工具通过监控游戏窗口中特定位置的像素颜色来检测对话界面。当检测到对话界面时，程序会模拟按键操作以自动点击对话选项。

程序使用Windows API的PrintWindow功能获取游戏窗口的截图，因此需要管理员权限才能正常工作。

## 自定义配置

如果需要调整检测点位置或颜色范围，可以修改源代码中的以下变量：

```python
# 点坐标结构（1920x1080分辨率下的坐标）
points = [
    (150, 66),  # M外圈左上
    (267, 57),  # M右下
    (155, 57),  # 隐藏对话按钮左上角
    (281, 60)   # 隐藏对话按钮右下角
]

# 定义颜色范围
color_ranges = [
    ColorRange(239, 243, 211, 215, 151, 155),  # 第一个点的颜色范围
    ColorRange(237, 241, 160, 164, 114, 118),  # 第二个点的颜色范围
    ColorRange(9, 13, 7, 11, 5, 9),
    ColorRange(9, 13, 7, 11, 4, 8)
]
```

## 从源码构建

如果要从源码构建可执行文件，可以使用以下命令：

```bash
# 安装PyInstaller
pip install pyinstaller

# 创建管理员权限清单文件
# 将项目中的admin_manifest.xml复制到当前目录

# 构建可执行文件
pyinstaller --noconfirm --onefile --name="星穹铁道自动对话" --manifest=admin_manifest.xml --hidden-import=win32gui --hidden-import=win32process --hidden-import=win32con --hidden-import=win32api --hidden-import=win32ui --strip main.py
```

## 致谢

感谢所有为本项目做出贡献的开发者和测试用户。