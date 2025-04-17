import os
import sys
import win32gui
import win32ui
import win32process
import win32con
import ctypes
import psutil
from ctypes.wintypes import RECT, POINT
from PIL import Image
import time
from typing import List


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


def capture_window(hwnd):
    """获取窗口截图，使用PrintWindow方法"""
    # 获取窗口信息
    try:
        info = get_window_info(hwnd)
    except Exception as e:
        return None
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
            result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
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


def set_foreground(hwnd):
    """激活窗口"""
    ctypes.windll.user32.SetForegroundWindow(hwnd)


def send_key(hwnd, key_code):
    """发送按键消息"""
    ctypes.windll.user32.PostMessageW(hwnd, win32con.WM_KEYDOWN, key_code, 0x210001)
    time.sleep(0.075)
    ctypes.windll.user32.PostMessageW(hwnd, win32con.WM_KEYUP, key_code, 0xC0210001)


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

    return None


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


# 以管理员权限重启程序
def restart_as_admin():
    if not is_admin():
        print("正在请求管理员权限...")
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
            print(f"请求管理员权限失败: {e}")
            input("按Enter键退出...")
            sys.exit(1)
