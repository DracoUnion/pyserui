# -*- coding: utf-8 -*-
"""
PySerUI - Python DirectUI Framework
Setup script for installation
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "PySerUI - Python DirectUI Framework"

setup(
    # 包名称
    name='pyserui',
    # 版本号
    version='1.0.0',
    # 作者信息
    author='wizardforcel',
    author_email='',
    # 许可证
    license='MIT',
    # 描述
    description='Python DirectUI Framework - 基于 pywin32 的 DirectUI 引擎',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    # 项目URL
    url='https://github.com/wizardforcel/pyserui',
    # 包目录
    packages=find_packages(),
    # Python版本要求
    python_requires='>=3.7',
    # 依赖项
    install_requires=[
        'pywin32>=227; platform_system=="Windows"',
    ],
    # 分类信息
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    # 关键词
    keywords='directui ui gui windows win32 gdiplus python',
    # 是否支持zip_safe
    zip_safe=False,
    # 包含数据文件
    include_package_data=True,
    # 项目依赖的额外信息
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
        ],
    },
    # 入口点（如果有命令行工具）
    entry_points={
        # 'console_scripts': [
        #     'pyserui-demo=pyserui.demo:main',
        # ],
    },
)
