from math import floor

import keyboard
import colorama

from core.cvutils import *
from core.window_utils import *
from core.debug_utils import *
import requests
from packaging import version

# 确保DPI感知
ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE

# 初始化彩色输出
colorama.init()

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

num_pos = (1727 - 490, 951 - 204)
# 490 204

cur_version = "0.4"

image_configs = {
    'dia_L_icon': {
        'pos': (141, 51),  # 相对窗口客户区的坐标
        'path': os.path.join(BASE_DIR, 'templates/dia_L.png'),  # 模板图片路径
        'threshold': 0.8  # 相似度阈值
    },
    'black_V_icon': {
        'pos': (945, 1021),  # 相对窗口客户区的坐标
        'path': os.path.join(BASE_DIR, 'templates/black_V.png'),  # 模板图片路径
        'threshold': 0.8  # 相似度阈值
    },
    'arrow_odd': {
        'pos': (1752 - 443, 866 - 113),  # 相对窗口客户区的坐标
        'path': os.path.join(BASE_DIR, 'templates/arrow_odd.png'),  # 模板图片路径
        'threshold': 0.75  # 相似度阈值
    },
    'arrow_even': {
        'pos': (1841 - 532, 956 - 203),  # 相对窗口客户区的坐标
        'path': os.path.join(BASE_DIR, 'templates/arrow_even.png'),  # 模板图片路径
        'threshold': 0.75  # 相似度阈值
    },
    'bubble_odd': {
        'pos': (1311, 745),  # 相对窗口客户区的坐标
        'path': os.path.join(BASE_DIR, 'templates/bubble_odd.png'),  # 模板图片路径
        'threshold': 0.7  # 相似度阈值
    },
    'bubble_even': {
        'pos': (1809 - 498, 947 - 283),  # 相对窗口客户区的坐标
        'path': os.path.join(BASE_DIR, 'templates/bubble_even.png'),  # 模板图片路径
        'threshold': 0.7  # 相似度阈值
    },
    'num1': {
        'pos': num_pos,  # 相对窗口客户区的坐标
        'path': os.path.join(BASE_DIR, 'templates/num1.png'),  # 模板图片路径
        'threshold': 0.7  # 相似度阈值
    },
    'num2': {
        'pos': num_pos,  # 相对窗口客户区的坐标
        'path': os.path.join(BASE_DIR, 'templates/num2.png'),  # 模板图片路径
        'threshold': 0.7  # 相似度阈值
    },
    'num3': {
        'pos': num_pos,  # 相对窗口客户区的坐标
        'path': os.path.join(BASE_DIR, 'templates/num3.png'),  # 模板图片路径
        'threshold': 0.7  # 相似度阈值
    },
    'num4': {
        'pos': num_pos,  # 相对窗口客户区的坐标
        'path': os.path.join(BASE_DIR, 'templates/num4.png'),  # 模板图片路径
        'threshold': 0.7  # 相似度阈值
    }
}


def check_for_update(current_version):
    try:
        response = requests.get(
            "http://39.105.210.187:5000/api/check-update",  # 我的更新服务器
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        latest_version = data['version']
        download_url = data['url']

        if version.parse(latest_version) > version.parse(current_version):
            print_info(f"新版本 {latest_version} 可用！ {download_url}")
        else:
            print_info("当前已是最新版本。")
    except requests.exceptions.RequestException as e:
        print_error(f"检查更新失败：{str(e)}")


def get_most_possible_num(offset, hwnd, window_info):
    results = [0.0] * 5
    for j in range(1, 5, 1):
        results[j] = check_image_match(hwnd, image_configs['num' + str(j)], window_info, True,
                                       (0, floor(-81.5 * offset)), False, True)
    return max(enumerate(results), key=lambda x: x[1])[0]


# 主函数
def main():
    if not is_admin():
        restart_as_admin()
    # 检查更新
    check_for_update(cur_version)
    print_info("程序启动")
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
    while True:
        hwnd = get_hwnd_by_pid(pid)
        if hwnd:
            window_info = get_window_info(hwnd)
            if window_info["window_size"][0] > 400:
                break
        time.sleep(0.2)

    print("\033[H\033[J")  # 清除等待消息
    print_info(f"Hwnd = 0x{hwnd:x}")

    # 获取详细窗口信息
    window_info = get_window_info(hwnd)
    print_info(f"窗口标题: {window_info['title']}")
    print_info(f"窗口大小: {window_info['window_size'][0]} X {window_info['window_size'][1]}")

    print_info("开始自动点击剧情中(当检测到进入剧情时会自动点击)...")
    print_info("按Ctrl+p键暂停/继续")
    # 预加载模板图像
    try:
        for cfg in image_configs.values():
            template = cv2.imread(cfg['path'])
            if template is None:
                print_error(f"无法加载模板图像: {cfg['path']}")
                continue
            cfg['cached_template'] = preprocess_image(template)

        print_info("模板图像预加载完成")
    except Exception as e:
        print_error(f"模板加载失败: {e}")

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
                try:
                    dia_L_match = check_image_match(hwnd, image_configs['dia_L_icon'], window_info)
                    black_V_match = check_image_match(hwnd, image_configs['black_V_icon'], window_info)
                    # 找箭头或气泡
                    # 这里要用同一张截图
                    # 因为可能在检测完某位之后选项才出现
                    img = capture_window(hwnd)
                    f = False
                    bubble_pos = -1
                    for i in range(0, 6, 1):
                        if i % 2 == 0:
                            arrow_match = check_image_match(hwnd,
                                                            image_configs['arrow_odd'],
                                                            window_info,
                                                            enable_offset=True,
                                                            offset=(0, floor(-81.5 * i)),
                                                            enable_debug=False,
                                                            img_input=img,
                                                            )
                            bubble_match = check_image_match(hwnd,
                                                             image_configs['bubble_odd'],
                                                             window_info,
                                                             enable_offset=True,
                                                             offset=(0, floor(-81.5 * i)),
                                                             enable_debug=False,
                                                             img_input=img,
                                                             )
                        else:
                            arrow_match = check_image_match(hwnd,
                                                            image_configs['arrow_even'],
                                                            window_info,
                                                            enable_offset=True,
                                                            offset=(0, floor(-163 * ((i - 1) / 2))),
                                                            enable_debug=False,
                                                            img_input=img,
                                                            )
                            bubble_match = check_image_match(hwnd,
                                                             image_configs['bubble_even'],
                                                             window_info,
                                                             enable_offset=True,
                                                             offset=(0, floor(-163 * ((i - 1) / 2))),
                                                             enable_debug=False,
                                                             img_input=img,
                                                             )

                        if bubble_match:
                            bubble_pos = i
                        if arrow_match:
                            f = True
                            print_info(f"检测到箭头,位置从下到上第{i + 1}个")
                            mx_idx = get_most_possible_num(i, hwnd, window_info)
                            set_foreground(hwnd)
                            send_key(hwnd, 0x30 + mx_idx)
                            break
                    if f:
                        continue
                    # 走到这里说明没有必选项
                    if bubble_pos != -1:  # 如果有选项
                        print_info(f"检测到气泡,位置从下到上第{bubble_pos + 1}个")
                        mx_idx = get_most_possible_num(bubble_pos, hwnd, window_info)
                        set_foreground(hwnd)
                        send_key(hwnd, 0x30 + mx_idx)
                        continue

                except Exception as e:
                    continue

                if dia_L_match or black_V_match:  # 说明只是普通对话，没有选项
                    if after_dialog > 0:
                        after_dialog = 0
                        print_info("检测到进入剧情对话")
                    # 发送按键
                    try:
                        set_foreground(hwnd)
                        send_key(hwnd, 0x20)
                        pass
                    except Exception as e:
                        pass
                elif after_dialog == 0:
                    after_dialog = 5
                    print_info("剧情对话结束")

            if after_dialog > 1:
                after_dialog -= 1
                try:
                    ctypes.windll.user32.ClipCursor(None)
                except Exception as e:
                    pass
            time.sleep(0.07)

    except KeyboardInterrupt:
        print_info("程序已退出")
    finally:
        print_info("清理资源...")
        try:
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
