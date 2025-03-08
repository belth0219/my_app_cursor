#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LangGPT提示词生成器启动脚本
用于启动LangGPT提示词生成器Web应用
"""

import os
import sys
import subprocess
import webbrowser
import time
import platform


def check_requirements():
    """检查是否安装了必要的依赖"""
    try:
        import flask

        return True
    except ImportError:
        return False


def install_requirements():
    """安装必要的依赖"""
    print("正在安装必要的依赖...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    print("依赖安装完成！")


def run_web_app():
    """运行Web应用"""
    # 检查langgpt_web_app.py是否存在
    if not os.path.exists("langgpt_web_app.py"):
        print("错误：找不到langgpt_web_app.py文件！")
        sys.exit(1)

    # 启动Web应用
    print("正在启动LangGPT提示词生成器Web应用...")

    # 根据操作系统选择不同的启动方式
    system = platform.system()
    process = None

    if system == "Windows":
        # Windows系统使用start命令在新窗口中启动
        subprocess.Popen(
            ["start", "cmd", "/k", sys.executable, "langgpt_web_app.py"], shell=True
        )
    else:
        # Linux/Mac系统使用nohup在后台运行
        with open("langgpt_web_app.log", "w") as log_file:
            process = subprocess.Popen(
                [sys.executable, "langgpt_web_app.py"],
                stdout=log_file,
                stderr=log_file,
                preexec_fn=os.setpgrp if system != "Windows" else None,
            )

    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)

    # 打开浏览器
    webbrowser.open("http://localhost:5000")

    print("LangGPT提示词生成器Web应用已启动！")
    print("如果浏览器没有自动打开，请手动访问：http://localhost:5000")

    if system != "Windows" and process is not None:
        print("\n要停止服务器，请按Ctrl+C或运行以下命令：")
        print(f"kill {process.pid}")


def main():
    """主函数"""
    print("=" * 50)
    print("LangGPT提示词生成器启动脚本")
    print("=" * 50)

    # 检查依赖
    if not check_requirements():
        print("未安装必要的依赖。")
        install = input("是否安装必要的依赖？(y/n): ").strip().lower()
        if install == "y":
            install_requirements()
        else:
            print("未安装依赖，无法启动应用。")
            sys.exit(1)

    # 运行Web应用
    run_web_app()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已中断")
        sys.exit(0)
