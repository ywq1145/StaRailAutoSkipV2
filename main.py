import time
import win32gui
import win32process
import win32ui
import ctypes
from ctypes.wintypes import RECT, POINT
from PIL import Image
import psutil
import keyboard
import colorama
from colorama import Fore, Style
import sys
import os

# 确保DPI感知
ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE

# 初始化彩色输出
colorama.init()

# 点坐标结构（1920x1080分辨率下的坐标）
points = [
    (150, 66),  # M外圈左上
    (267, 57),  # M右下
    (155, 57),  # 隐藏对话按钮左上角
    (281, 60)  # 隐藏对话按钮右下角
]


# 颜色范围结构
class ColorRange:
    def __init__(self, r_min, r_max, g_min, g_max, b_min, b_max):
        self.r_min, self.r_max = r_min, r_max
        self.g_min, self.g_max = g_min, g_max
        self.b_min, self.b_max = b_min, b_max


# 定义颜色范围
color_ranges = [
    ColorRange(239, 243, 211, 215, 151, 155),  # 第一个点的颜色范围
    ColorRange(237, 241, 160, 164, 114, 118),  # 第二个点的颜色范围
    ColorRange(9, 13, 7, 11, 5, 9),
    ColorRange(9, 13, 7, 11, 4, 8)
]


# 打印带颜色的信息
def print_info(message):
    print(f"{Style.BRIGHT}{Fore.GREEN}[Info] {message}{Style.RESET_ALL}")


def print_error(message):
    print(f"{Style.BRIGHT}{Fore.RED}[Error] {message}{Style.RESET_ALL}")


def print_waiting(message):
    print(f"{Style.BRIGHT}{Fore.YELLOW}[Waiting] {message}{Style.RESET_ALL}", end='\r')


# 注释掉调试信息打印函数
# def print_debug(message):
#     print(f"{Style.BRIGHT}{Fore.LIGHTBLACK_EX}[Debug] {message}{Style.RESET_ALL}")

# 检查程序是否以管理员权限运行
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


# 以管理员权限重启程序
def restart_as_admin():
    if not is_admin():
        print_info("正在请求管理员权限...")
        try:
            # 使用Python执行文件路径或打包后的exe路径
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe
                script = sys.executable
            else:
                # 如果是Python脚本
                script = os.path.abspath(sys.argv[0])

            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)
            sys.exit()
        except Exception as e:
            print_error(f"请求管理员权限失败: {e}")
            input("按Enter键退出...")
            sys.exit(1)


# 获取窗口的详细信息
def get_window_info(hwnd):
    """获取窗口的详细信息，包括边框和客户区域"""
    # 获取整个窗口大小（包括边框）
    window_rect = RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(window_rect))

    # 获取客户区域大小（不包括边框）
    client_rect = RECT()
    ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(client_rect))

    # 转换客户区域坐标到屏幕坐标
    pt_top_left = POINT(client_rect.left, client_rect.top)
    pt_bottom_right = POINT(client_rect.right, client_rect.bottom)
    ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(pt_top_left))
    ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(pt_bottom_right))

    # 计算各种尺寸
    window_width = window_rect.right - window_rect.left
    window_height = window_rect.bottom - window_rect.top
    client_width = client_rect.right - client_rect.left
    client_height = client_rect.bottom - client_rect.top

    # 计算边框大小
    border_left = pt_top_left.x - window_rect.left
    border_top = pt_top_left.y - window_rect.top

    # 获取窗口标题和类名
    title_length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    title_buffer = ctypes.create_unicode_buffer(title_length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)

    return {
        "hwnd": hwnd,
        "window_rect": (window_rect.left, window_rect.top, window_rect.right, window_rect.bottom),
        "client_rect": (client_rect.left, client_rect.top, client_rect.right, client_rect.bottom),
        "window_size": (window_width, window_height),
        "client_size": (client_width, client_height),
        "border": (border_left, border_top),
        "title": title_buffer.value
    }


# 检查颜色是否在指定范围内
def is_color_in_range(color, color_range):
    r, g, b = color
    return (color_range.r_min <= r <= color_range.r_max and
            color_range.g_min <= g <= color_range.g_max and
            color_range.b_min <= b <= color_range.b_max)


# 获取窗口截图 (使用PrintWindow方法)
def capture_window(hwnd):
    """获取窗口截图，使用PrintWindow方法"""
    # 获取窗口信息
    info = get_window_info(hwnd)
    width, height = info["window_size"]

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # 使用不同的PrintWindow参数尝试获取窗口内容
    best_result = 0
    best_image = None

    # 遍历所有可能的PrintWindow参数
    for flag in [3, 2, 1, 0]:  # 优先尝试更全面的选项
        try:
            result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), flag)
            if result > best_result:
                best_result = result

                # 转换为PIL图像
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                best_image = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1)

                # 如果成功了，就不再尝试其他参数
                if result == 1:
                    break
        except:
            pass

    # 清理资源
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if best_image is None:
        return Image.new('RGB', (width, height), (0, 0, 0))

    return best_image


# 检查多个像素点
def check_multiple_pixels(hwnd, points, color_ranges):
    match_count = 0

    # 获取窗口截图
    img = capture_window(hwnd)

    # 检查每个点的颜色
    for i, (x, y) in enumerate(points):
        # 确保坐标在截图范围内
        if 0 <= x < img.width and 0 <= y < img.height:
            try:
                color = img.getpixel((x, y))
                if is_color_in_range(color, color_ranges[i]):
                    match_count += 1
            except:
                pass

    return match_count >= 3


# 根据实际的分辨率大小调整坐标点
def init_points(window_info):
    width, height = window_info["client_size"]

    if (width * 9) > (height * 16):
        scale = height / 1080.0
    else:
        scale = width / 1920.0

    scaled_points = []
    for x, y in points:
        scaled_points.append((int(round(x * scale)), int(round(y * scale))))

    return scaled_points


# 获取进程PID
def get_pid(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == process_name.lower():
            return proc.info['pid']
    return None


# 获取进程的主窗口句柄
def get_hwnd_by_pid(pid):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)

    # 尝试找到主窗口
    for hwnd in hwnds:
        info = get_window_info(hwnd)
        if info["window_size"][0] > 400 and info["window_size"][1] > 300:
            return hwnd

    # 如果没有找到合适的窗口，返回第一个
    return hwnds[0] if hwnds else None


# 主函数
def main():
    # 检查管理员权限
    if not is_admin():
        restart_as_admin()

    print_info("程序启动（管理员模式）")
    print_waiting("正在等待崩铁进程 StarRail.exe")

    # 等待进程
    pid = None
    while not pid:
        pid = get_pid("StarRail.exe")
        if not pid:
            time.sleep(0.2)

    print("\r", end="")  # 清除等待消息
    print_info(f"Pid = {pid}")

    print_waiting("正在等待崩铁窗口")

    # 等待窗口
    hwnd = None
    while True:
        hwnd = get_hwnd_by_pid(pid)
        if hwnd:
            window_info = get_window_info(hwnd)
            if window_info["window_size"][0] > 400:
                break
        time.sleep(0.2)

    print("\r", end="")  # 清除等待消息
    print_info(f"Hwnd = 0x{hwnd:x}")

    # 获取详细窗口信息
    window_info = get_window_info(hwnd)
    print_info(f"窗口标题: {window_info['title']}")
    print_info(f"窗口大小: {window_info['window_size'][0]} X {window_info['window_size'][1]}")

    # 调整坐标点
    scaled_points = init_points(window_info)

    print_info("开始自动点击剧情中(当检测到进入剧情时会自动点击)...")
    print_info("按Ctrl+p键暂停/继续")

    is_active = True

    # afterDialog：值为0表示正在剧情对话中，值为1表示不在剧情对话中，大于1表示剧情对话刚刚结束
    after_dialog = 1

    try:
        while True:
            # 检测Ctrl+P暂停/继续
            if keyboard.is_pressed('ctrl+p'):
                is_active = not is_active
                if is_active:
                    print_info(f"程序继续{Fore.GREEN}执行{Style.RESET_ALL}中")
                else:
                    print_info(f"程序{Fore.YELLOW}暂停{Style.RESET_ALL}中")
                time.sleep(0.4)

            if is_active:
                # 检测结果
                result = check_multiple_pixels(hwnd, scaled_points, color_ranges)

                if result:
                    if after_dialog > 0:
                        after_dialog = 0
                        print_info("检测到进入剧情对话")

                    # 发送按键
                    win32gui.SetForegroundWindow(hwnd)
                    keyboard.press_and_release('1')
                    time.sleep(0.075)
                    keyboard.press_and_release('space')

                elif after_dialog == 0:
                    after_dialog = 16
                    print_info("剧情对话结束")

            # 解除鼠标锁定
            if after_dialog > 1:
                after_dialog -= 1
                ctypes.windll.user32.ClipCursor(None)

            time.sleep(0.125)

    except KeyboardInterrupt:
        print_info("程序已退出")
    finally:
        print_info("清理资源...")
        try:
            # 确保解除鼠标锁定
            ctypes.windll.user32.ClipCursor(None)
        except:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_error(f"程序异常: {e}")
        import traceback

        traceback.print_exc()
        input("按Enter键退出...")