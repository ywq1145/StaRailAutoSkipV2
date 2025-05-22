import cv2
import numpy as np

from core.window_utils import capture_window


def preprocess_image(image):
    """图像预处理流程"""
    if len(image.shape) == 2:  # 如果已经是灰度图
        gray = image
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return edges


def calculate_similarity(template, target):
    """使用模板匹配计算相似度"""
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    # similarity = result[0][0]  # 范围[-1,1]，1表示完全匹配
    min_val, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val  # 转换为[0,1]范围


def check_image_match(hwnd, config, window_info, enable_offset=False, offset=(0, 0), enable_debug=False,
                      return_sim=False, img_input=None):
    """
    图像匹配检测函数
    config需要包含：
    - 'pos': 相对窗口客户区的(x, y)
    - 'cached_template': 预处理的模板图像
    - 'threshold': 相似度阈值
    """
    # 获取窗口截图（使用原有capture_window方法）
    if img_input is not None:
        full_image = img_input
    else:
        full_image = capture_window(hwnd)

    # 转换为OpenCV格式
    screen_cv = cv2.cvtColor(np.array(full_image), cv2.COLOR_RGB2BGR)

    # 计算相对客户区的坐标
    border_left, border_top = window_info["border"]
    x_offset = config['pos'][0] + border_left
    y_offset = config['pos'][1] + border_top
    if enable_offset:
        x_offset += offset[0]
        y_offset += offset[1]

    # 获取模板尺寸
    template_h, template_w = config['cached_template'].shape[:2]

    # 提取目标区域
    target_region = screen_cv[
                    y_offset:y_offset + template_h,
                    x_offset:x_offset + template_w
                    ]

    # 预处理图像
    processed_screen = preprocess_image(target_region)

    if enable_debug:
        cv2.imwrite('processed_screen.png', target_region)

    if return_sim:
        return calculate_similarity(config['cached_template'], preprocess_image(target_region))

    # 计算相似度
    similarity = calculate_similarity(config['cached_template'], processed_screen)
    if similarity >= 0.5 and enable_debug:
        print(f"Similarity: {similarity}")

    return similarity >= config['threshold']
