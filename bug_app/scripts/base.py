# base.py
import os
import sys
import django

# 导入 Django 模块

# Django 是一个基于 Python 的 Web 开发框架，可以帮助开发者快速构建 Web 应用程序。
# 在使用 Django 开发项目时，需要首先配置 Django 环境，以便能够正确导入 Django 模块，并进行数据库操作等相关操作。

# 设置 Django 项目的根目录

# Django 项目的根目录是指包含 settings.py 文件的目录，它通常是整个项目的根目录。
# 这个根目录可能会随着项目的不同而变化，因此需要通过动态获取的方式来确定。

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 使用 os.path.abspath(__file__) 获取当前脚本文件的绝对路径，即该脚本文件在文件系统中的实际路径。
# 使用 os.path.dirname() 获取当前脚本文件所在目录的父级目录，即项目的根目录。
# 使用两次 os.path.dirname() 是因为在一般的 Django 项目中，脚本文件通常放在项目的子目录中，而不是直接放在根目录下。

sys.path.append(base_dir)

# 将项目的根目录添加到 sys.path 中，以便 Python 解释器能够找到该目录下的模块文件。
# sys.path 是 Python 解释器搜索模块的路径列表，将项目根目录添加到其中后，就可以正确导入项目中的其他模块。

# 设置 Django 的环境变量

# Django 使用环境变量 DJANGO_SETTINGS_MODULE 来确定项目的设置文件路径。
# 在进行 Django 相关操作之前，需要设置该环境变量，以确保 Django 能够正确加载项目的设置文件。

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bug_tracer.settings")

# 使用 os.environ.setdefault() 方法设置环境变量 DJANGO_SETTINGS_MODULE 的值为 "bug_tracer.settings"。
# 这里的 "bug_tracer.settings" 是指项目的设置文件路径，其中 "bug_tracer" 是项目的名称，"settings" 是设置文件的模块名。

django.setup()

# 调用 django.setup() 方法，初始化 Django 环境。
# 这个方法会加载项目的设置文件，并初始化 Django 应用程序，以便能够正常使用 Django 的各种功能。
