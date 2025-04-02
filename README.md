# 星穹铁道自动对话工具

## 安装与使用

1. 从[Releases](https://github.com/yourusername/StarRailAuto/releases)页面下载最新版本的`星穹铁道自动对话.exe`
2. 双击运行，会自动请求管理员权限
3. 程序会自动等待星穹铁道游戏启动

## 注意事项

后台也可以自动点击，但别最小化。

## 自定义配置

如果需要调整检测点位置或颜色范围，可以修改源代码中的以下变量：

```python
# 点坐标结构（1920x1080分辨率下的坐标），随便找几个能够标识对话状态的点
points = [
    (150, 66),  
    (267, 57),  
    (155, 57),  
    (281, 60)   
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

代码参考[SyrieYume/GenshinAutoV2: 原神后台自动点剧情工具 v2版本。](https://github.com/SyrieYume/GenshinAutoV2)