# -*- coding:UTF-8 -*-

# author:
# contact:
# datetime:
# software: PyCharm

"""
文件说明：
打印工程目录文件，参考链接：
https://blog.csdn.net/albertsh/article/details/77886876
"""

import os
import os.path


def dfs_showdir(path, depth):
    if depth == 0:
        print("root:[" + path + "]")
    # print("当前文件路径是{}，包含文件有{}。".format(path, os.listdir(path)))

    for item in os.listdir(path):
        print("| " * depth + "+--" + item)
        if item in [
            ".git",
            ".idea",
            "__pycache__",
            ".vscode",
            "node_modules",
            ".venv",
            "server",
            "scripts",
        ]:
            continue

        new_item = path + "/" + item
        if depth > 3:
            return
        if os.path.isdir(new_item):
            dfs_showdir(new_item, depth + 1)


if __name__ == "__main__":
    dfs_showdir(".", 0)
