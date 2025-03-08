#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LangGPT提示词生成器
一个简单的命令行工具，用于生成符合LangGPT格式的提示词
"""

import os
import sys
import argparse
from typing import Dict, List, Optional, Union, Any


class LangGPTGenerator:
    """LangGPT提示词生成器类"""

    def __init__(self):
        self.template = {
            "role": "",
            "profile": {
                "author": "",
                "version": "1.0",
                "language": "中文",
                "description": "",
            },
            "skills": [],
            "background": "",
            "goals": [],
            "output_format": "",
            "rules": [],
            "workflows": [],
            "commands": {"prefix": "/", "commands": {}},
            "initialization": "",
        }

    def interactive_mode(self) -> None:
        """交互式模式，引导用户填写各个部分"""
        print("欢迎使用LangGPT提示词生成器！")
        print("本工具将引导你创建一个符合LangGPT格式的提示词。")
        print("请按照提示填写各个部分，按Enter键确认。")
        print("如果某个部分是可选的，你可以直接按Enter跳过。")
        print("-" * 50)

        # 角色名称
        self.template["role"] = input("请输入角色名称: ").strip()

        # 配置文件
        self.template["profile"]["author"] = (
            input("请输入作者名称 (默认: AI助手): ").strip() or "AI助手"
        )
        self.template["profile"]["version"] = (
            input("请输入版本号 (默认: 1.0): ").strip() or "1.0"
        )
        self.template["profile"]["language"] = (
            input("请输入语言 (默认: 中文): ").strip() or "中文"
        )
        self.template["profile"]["description"] = input("请输入角色描述: ").strip()

        # 技能
        print("\n请输入角色的技能列表，每行一个技能，输入空行结束:")
        while True:
            skill = input("- ").strip()
            if not skill:
                break
            self.template["skills"].append(skill)

        # 背景信息
        print("\n请输入背景信息 (可选，输入空行跳过):")
        background_lines = []
        while True:
            line = input()
            if not line and not background_lines:
                break
            if not line and background_lines:
                self.template["background"] = "\n".join(background_lines)
                break
            background_lines.append(line)

        # 目标
        print("\n请输入角色的目标列表，每行一个目标，输入空行结束 (可选):")
        while True:
            goal = input("- ").strip()
            if not goal:
                break
            self.template["goals"].append(goal)

        # 输出格式
        print("\n请输入输出格式要求 (可选，输入空行跳过):")
        output_format_lines = []
        while True:
            line = input()
            if not line and not output_format_lines:
                break
            if not line and output_format_lines:
                self.template["output_format"] = "\n".join(output_format_lines)
                break
            output_format_lines.append(line)

        # 规则
        print("\n请输入规则列表，每行一个规则，输入空行结束:")
        rule_num = 1
        while True:
            rule = input(f"{rule_num}. ").strip()
            if not rule:
                break
            self.template["rules"].append(rule)
            rule_num += 1

        # 工作流程
        print("\n请输入工作流程列表，每行一个步骤，输入空行结束:")
        workflow_num = 1
        while True:
            workflow = input(f"{workflow_num}. ").strip()
            if not workflow:
                break
            self.template["workflows"].append(workflow)
            workflow_num += 1

        # 命令
        add_commands = input("\n是否添加命令? (y/n, 默认: n): ").strip().lower() == "y"
        if add_commands:
            self.template["commands"]["prefix"] = (
                input("请输入命令前缀 (默认: /): ").strip() or "/"
            )
            print("请输入命令列表，格式为 '命令名: 命令描述'，输入空行结束:")
            while True:
                command_input = input("- ").strip()
                if not command_input:
                    break
                try:
                    cmd_name, cmd_desc = command_input.split(":", 1)
                    self.template["commands"]["commands"][
                        cmd_name.strip()
                    ] = cmd_desc.strip()
                except ValueError:
                    print("格式错误，请使用 '命令名: 命令描述' 的格式")

        # 初始化
        print("\n请输入初始化指令:")
        initialization_lines = []
        while True:
            line = input()
            if not line and initialization_lines:
                self.template["initialization"] = "\n".join(initialization_lines)
                break
            initialization_lines.append(line)

    def generate_prompt(self) -> str:
        """生成LangGPT格式的提示词"""
        prompt = f"# Role: {self.template['role']}\n\n"

        # 配置文件
        prompt += "## Profile\n"
        prompt += f"- author: {self.template['profile']['author']}\n"
        prompt += f"- version: {self.template['profile']['version']}\n"
        prompt += f"- language: {self.template['profile']['language']}\n"
        prompt += f"- description: {self.template['profile']['description']}\n\n"

        # 技能
        if self.template["skills"]:
            prompt += "## Skills\n"
            for skill in self.template["skills"]:
                prompt += f"- {skill}\n"
            prompt += "\n"

        # 背景信息
        if self.template["background"]:
            prompt += "## Background\n"
            prompt += f"{self.template['background']}\n\n"

        # 目标
        if self.template["goals"]:
            prompt += "## Goals\n"
            for goal in self.template["goals"]:
                prompt += f"- {goal}\n"
            prompt += "\n"

        # 输出格式
        if self.template["output_format"]:
            prompt += "## OutputFormat\n"
            prompt += f"{self.template['output_format']}\n\n"

        # 规则
        if self.template["rules"]:
            prompt += "## Rules\n"
            for i, rule in enumerate(self.template["rules"], 1):
                prompt += f"{i}. {rule}\n"
            prompt += "\n"

        # 工作流程
        if self.template["workflows"]:
            prompt += "## Workflows\n"
            for i, workflow in enumerate(self.template["workflows"], 1):
                prompt += f"{i}. {workflow}\n"
            prompt += "\n"

        # 命令
        if self.template["commands"]["commands"]:
            prompt += "## Commands\n"
            prompt += f"- Prefix: \"{self.template['commands']['prefix']}\"\n"
            prompt += "- Commands:\n"
            for cmd_name, cmd_desc in self.template["commands"]["commands"].items():
                prompt += f"    - {cmd_name}: {cmd_desc}\n"
            prompt += "\n"

        # 初始化
        if self.template["initialization"]:
            prompt += "## Initialization\n"
            prompt += f"{self.template['initialization']}\n"

        return prompt

    def save_to_file(self, filename: str) -> None:
        """将生成的提示词保存到文件"""
        prompt = self.generate_prompt()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"提示词已保存到文件: {filename}")

    def print_prompt(self) -> None:
        """打印生成的提示词"""
        prompt = self.generate_prompt()
        print("\n" + "=" * 50)
        print("生成的LangGPT提示词:")
        print("=" * 50)
        print(prompt)


def main():
    parser = argparse.ArgumentParser(description="LangGPT提示词生成器")
    parser.add_argument("-o", "--output", help="输出文件名")
    args = parser.parse_args()

    generator = LangGPTGenerator()
    generator.interactive_mode()

    if args.output:
        generator.save_to_file(args.output)
    else:
        generator.print_prompt()
        save_option = input("\n是否保存到文件? (y/n, 默认: n): ").strip().lower()
        if save_option == "y":
            filename = input("请输入文件名: ").strip()
            if not filename:
                filename = (
                    f"{generator.template['role'].replace(' ', '_').lower()}_prompt.md"
                )
            generator.save_to_file(filename)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已中断")
        sys.exit(0)
