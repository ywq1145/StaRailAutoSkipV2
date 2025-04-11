# 打印带颜色的信息
from colorama import Fore, Style


def print_info(message):
    print(f"{Style.BRIGHT}{Fore.GREEN}[Info] {message}{Style.RESET_ALL}")


def print_error(message):
    print(f"{Style.BRIGHT}{Fore.RED}[Error] {message}{Style.RESET_ALL}")


def print_waiting(message):
    print(f"{Style.BRIGHT}{Fore.YELLOW}[Waiting] {message}{Style.RESET_ALL}", end='\r')


def print_debug(message):
    print(f"{Style.BRIGHT}{Fore.LIGHTBLACK_EX}[Debug] {message}{Style.RESET_ALL}")
