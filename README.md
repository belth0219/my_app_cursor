# LangGPT 提示词生成工具

这是一个用于创建符合 LangGPT 格式的结构化提示词的工具集合。LangGPT 是一种将提示词组织成结构化格式的方法，可以帮助你创建更加清晰、可重用和高效的提示词。

## 项目内容

本项目包含以下文件：

1. **cursor_langgpt_generator.md** - 一个 Cursor LangGPT 提示词生成助手的规则文件，可以在 Cursor 中使用
2. **langgpt_example_programming_mentor.md** - 一个使用 LangGPT 格式的编程学习导师角色示例
3. **langgpt_generator.py** - 一个命令行工具，用于交互式生成 LangGPT 格式的提示词
4. **cursor_langgpt_rules.md** - 一个基础的 Cursor 编程助手规则文件
5. **cursor_advanced_langgpt_rules.md** - 一个高级的 Cursor 编程助手规则文件，包含更多 Cursor 特定功能

## LangGPT 格式介绍

LangGPT 是一种结构化的提示词编写方法，它将提示词组织成类似编程语言的结构，包括以下主要部分：

- **Role**: 定义 AI 助手的角色
- **Profile**: 角色的基本信息，如作者、版本、语言和描述
- **Skills**: 角色应具备的技能列表
- **Background**: 角色的背景信息（可选）
- **Goals**: 角色的目标列表（可选）
- **OutputFormat**: 输出格式要求（可选）
- **Rules**: 角色应遵循的规则列表
- **Workflows**: 角色处理问题的工作流程
- **Commands**: 用户可以使用的命令（可选）
- **Initialization**: 初始化指令，包括角色的自我介绍

## 使用方法

### 1. 使用命令行工具生成提示词

```bash
python langgpt_generator.py [-o 输出文件名]
```

这将启动交互式提示词生成过程，引导你填写各个部分。完成后，可以选择将生成的提示词保存到文件或直接显示在控制台。

### 2. 使用 Cursor LangGPT 提示词生成助手

将`cursor_langgpt_generator.md`文件的内容复制到 Cursor 中，然后按照助手的引导创建 LangGPT 格式的提示词。

### 3. 参考示例文件

查看`langgpt_example_programming_mentor.md`文件，了解 LangGPT 格式的实际应用示例。

### 4. 使用 Cursor 编程助手规则文件

- 基础版：使用`cursor_langgpt_rules.md`文件的内容
- 高级版：使用`cursor_advanced_langgpt_rules.md`文件的内容，包含更多 Cursor 特定功能

## LangGPT 模板

```markdown
# Role: {角色名称}

## Profile

- author: {作者}
- version: {版本号}
- language: {语言}
- description: {角色描述}

## Skills

- {技能 1}
- {技能 2}
- {技能 3}
  ...

## Background(可选)

{背景信息}

## Goals(可选)

- {目标 1}
- {目标 2}
  ...

## OutputFormat(可选)

{输出格式要求}

## Rules

1. {规则 1}
2. {规则 2}
   ...

## Workflows

1. {工作流程 1}
2. {工作流程 2}
   ...

## Commands(可选)

- Prefix: "{命令前缀}"
- Commands:
  - {命令 1}: {命令 1 描述}
  - {命令 2}: {命令 2 描述}
    ...

## Initialization

{初始化指令}
```

## 为什么使用 LangGPT 格式？

- **结构化**：清晰的结构使提示词更易于理解和维护
- **可重用**：模块化设计使得提示词的各个部分可以重用
- **可扩展**：容易添加新的功能和规则
- **一致性**：确保 AI 助手的回答风格和质量一致
- **可控性**：通过明确的规则和工作流程，更好地控制 AI 助手的行为

## 贡献

欢迎提出建议和改进意见！如果你有任何问题或想法，请随时提出。

## 许可

MIT
