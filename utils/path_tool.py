"""
为整个工程提供统一的绝对路径
"""
import os


def get_project_root() -> str:
    """
    获取工程所在根目录
    :return: 字符串根目录
    """

    # 获取当前文件绝对路径
    current_dir = os.path.dirname(__file__)
    # 获取工程根目录
    project_root = os.path.abspath(os.path.join(current_dir, ".."))

    return project_root


def get_abs_path(relative_path: str) -> str:
    """
    传递相对路径，得到绝对路径
    :param relative_path:相对路径
    :return: 绝对路径
    """
    return os.path.join(get_project_root(), relative_path)


if __name__ == '__main__':
    print(get_project_root())
    print(get_abs_path(__file__))
