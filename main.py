import os
import sys
from typing import Dict, List, Optional


class LangGPTPromptGenerator:
    """
    LangGPT格式的prompt生成助手
    """

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
            "commands": {
                "prefix": "/",
                "commands": {
                    "help": "这意味着用户不知道命令的用法。请介绍自己和命令的用法。",
                    "continue": "这意味着您的输出被截断。请继续您离开的地方。",
                },
            },
            "init": "",
        }

    def set_role(self, role: str) -> None:
        """设置角色名称"""
        self.template["role"] = role

    def set_profile(
        self,
        author: str,
        version: str = "1.0",
        language: str = "中文",
        description: str = "",
    ) -> None:
        """设置角色配置文件"""
        self.template["profile"]["author"] = author
        self.template["profile"]["version"] = version
        self.template["profile"]["language"] = language
        self.template["profile"]["description"] = description

    def add_skills(self, skills: List[str]) -> None:
        """添加技能列表"""
        self.template["skills"].extend(skills)

    def set_background(self, background: str) -> None:
        """设置背景信息"""
        self.template["background"] = background

    def add_goals(self, goals: List[str]) -> None:
        """添加目标列表"""
        self.template["goals"].extend(goals)

    def set_output_format(self, output_format: str) -> None:
        """设置输出格式"""
        self.template["output_format"] = output_format

    def add_rules(self, rules: List[str]) -> None:
        """添加规则列表"""
        self.template["rules"].extend(rules)

    def add_workflows(self, workflows: List[str]) -> None:
        """添加工作流程列表"""
        self.template["workflows"].extend(workflows)

    def add_commands(self, commands: Dict[str, str]) -> None:
        """添加命令"""
        self.template["commands"]["commands"].update(commands)

    def set_init(self, init: str) -> None:
        """设置初始化文本"""
        self.template["init"] = init

    def generate_default_init(self) -> str:
        """生成默认的初始化文本"""
        return f"作为一个<Role>，你必须遵循<Rules>，你必须使用默认的<Language>与用户交流，你必须向用户问好。然后介绍自己并介绍<Workflow>。"

    def generate_prompt(self) -> str:
        """生成LangGPT格式的prompt"""
        if not self.template["init"]:
            self.template["init"] = self.generate_default_init()

        prompt = f"# Role: {self.template['role']}\n\n"

        # 添加Profile部分
        prompt += "## Profile\n"
        prompt += f"- author: {self.template['profile']['author']}\n"
        prompt += f"- version: {self.template['profile']['version']}\n"
        prompt += f"- language: {self.template['profile']['language']}\n"
        prompt += f"- description: {self.template['profile']['description']}\n\n"

        # 添加Skills部分
        if self.template["skills"]:
            prompt += "## Skills\n"
            for skill in self.template["skills"]:
                prompt += f"- {skill}\n"
            prompt += "\n"

        # 添加Background部分
        if self.template["background"]:
            prompt += "## Background\n"
            prompt += f"{self.template['background']}\n\n"

        # 添加Goals部分
        if self.template["goals"]:
            prompt += "## Goals\n"
            for goal in self.template["goals"]:
                prompt += f"- {goal}\n"
            prompt += "\n"

        # 添加OutputFormat部分
        if self.template["output_format"]:
            prompt += "## OutputFormat\n"
            prompt += f"{self.template['output_format']}\n\n"

        # 添加Rules部分
        if self.template["rules"]:
            prompt += "## Rules\n"
            for i, rule in enumerate(self.template["rules"], 1):
                prompt += f"{i}. {rule}\n"
            prompt += "\n"

        # 添加Workflows部分
        if self.template["workflows"]:
            prompt += "## Workflows\n"
            for i, workflow in enumerate(self.template["workflows"], 1):
                prompt += f"{i}. {workflow}\n"
            prompt += "\n"

        # 添加Commands部分
        if self.template["commands"]["commands"]:
            prompt += "## Commands\n"
            prompt += f"- Prefix: \"{self.template['commands']['prefix']}\"\n"
            prompt += "- Commands:\n"
            for cmd, desc in self.template["commands"]["commands"].items():
                prompt += f"    - {cmd}: {desc}\n"
            prompt += "\n"

        # 添加Init部分
        prompt += "## Initialization\n"
        prompt += f"{self.template['init']}\n"

        return prompt


def main():
    print("欢迎使用LangGPT Prompt生成助手！")
    print("这个工具将帮助您创建符合LangGPT格式的结构化prompt。")

    generator = LangGPTPromptGenerator()

    # 收集基本信息
    role = input("请输入角色名称: ")
    generator.set_role(role)

    author = input("请输入作者名称: ")
    language = input("请输入语言(默认为中文): ") or "中文"
    description = input("请输入角色描述: ")
    generator.set_profile(author, language=language, description=description)

    # 收集技能
    print("\n请输入角色技能(每行一个，输入空行结束):")
    skills = []
    while True:
        skill = input()
        if not skill:
            break
        skills.append(skill)
    generator.add_skills(skills)

    # 收集背景信息
    background = input("\n请输入背景信息(可选): ")
    if background:
        generator.set_background(background)

    # 收集目标
    print("\n请输入目标(每行一个，输入空行结束):")
    goals = []
    while True:
        goal = input()
        if not goal:
            break
        goals.append(goal)
    generator.add_goals(goals)

    # 收集输出格式
    output_format = input("\n请输入输出格式(可选): ")
    if output_format:
        generator.set_output_format(output_format)

    # 收集规则
    print("\n请输入规则(每行一个，输入空行结束):")
    rules = []
    while True:
        rule = input()
        if not rule:
            break
        rules.append(rule)
    generator.add_rules(rules)

    # 收集工作流程
    print("\n请输入工作流程(每行一个，输入空行结束):")
    workflows = []
    while True:
        workflow = input()
        if not workflow:
            break
        workflows.append(workflow)
    generator.add_workflows(workflows)

    # 生成prompt
    prompt = generator.generate_prompt()

    print("\n生成的LangGPT格式Prompt如下:")
    print("=" * 50)
    print(prompt)
    print("=" * 50)

    # 保存到文件
    save = input("\n是否保存到文件? (y/n): ")
    if save.lower() == "y":
        filename = (
            input("请输入文件名(默认为 'langgpt_prompt.txt'): ") or "langgpt_prompt.txt"
        )
        with open(filename, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"Prompt已保存到 {filename}")


if __name__ == "__main__":
    main()
