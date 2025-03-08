#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LangGPT提示词生成器Web应用
一个基于Flask的Web应用，用于在浏览器中生成符合LangGPT格式的提示词
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# 确保templates目录存在
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)


# 创建HTML模板
@app.route("/create_templates", methods=["GET"])
def create_templates():
    # 创建index.html
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(
            """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGPT提示词生成器</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <h1>LangGPT提示词生成器</h1>
            <p>创建符合LangGPT格式的结构化提示词</p>
        </header>
        
        <div class="main-content">
            <div class="form-container">
                <form id="langGptForm">
                    <div class="section">
                        <h2>基本信息</h2>
                        <div class="form-group">
                            <label for="role">角色名称 *</label>
                            <input type="text" id="role" name="role" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="author">作者</label>
                            <input type="text" id="author" name="author" value="AI助手">
                        </div>
                        
                        <div class="form-group">
                            <label for="version">版本</label>
                            <input type="text" id="version" name="version" value="1.0">
                        </div>
                        
                        <div class="form-group">
                            <label for="language">语言</label>
                            <input type="text" id="language" name="language" value="中文">
                        </div>
                        
                        <div class="form-group">
                            <label for="description">角色描述 *</label>
                            <textarea id="description" name="description" rows="3" required></textarea>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>技能</h2>
                        <div class="form-group">
                            <label for="skills">技能列表 (每行一个) *</label>
                            <textarea id="skills" name="skills" rows="5" required></textarea>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>背景信息 (可选)</h2>
                        <div class="form-group">
                            <textarea id="background" name="background" rows="5"></textarea>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>目标 (可选)</h2>
                        <div class="form-group">
                            <label for="goals">目标列表 (每行一个)</label>
                            <textarea id="goals" name="goals" rows="5"></textarea>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>输出格式 (可选)</h2>
                        <div class="form-group">
                            <textarea id="outputFormat" name="outputFormat" rows="5"></textarea>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>规则</h2>
                        <div class="form-group">
                            <label for="rules">规则列表 (每行一个) *</label>
                            <textarea id="rules" name="rules" rows="5" required></textarea>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>工作流程</h2>
                        <div class="form-group">
                            <label for="workflows">工作流程 (每行一个) *</label>
                            <textarea id="workflows" name="workflows" rows="5" required></textarea>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>命令 (可选)</h2>
                        <div class="form-group">
                            <label for="commandPrefix">命令前缀</label>
                            <input type="text" id="commandPrefix" name="commandPrefix" value="/">
                        </div>
                        
                        <div class="form-group">
                            <label for="commands">命令列表 (格式: 命令名: 命令描述)</label>
                            <textarea id="commands" name="commands" rows="5"></textarea>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>初始化</h2>
                        <div class="form-group">
                            <label for="initialization">初始化指令 *</label>
                            <textarea id="initialization" name="initialization" rows="5" required></textarea>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn-primary">生成提示词</button>
                        <button type="button" id="copyBtn" class="btn-secondary" disabled>复制到剪贴板</button>
                        <button type="button" id="downloadBtn" class="btn-secondary" disabled>下载为文件</button>
                        <button type="reset" class="btn-danger">重置表单</button>
                    </div>
                </form>
            </div>
            
            <div class="result-container">
                <h2>生成的提示词</h2>
                <pre id="result"></pre>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>"""
        )

    # 创建CSS样式
    with open("static/style.css", "w", encoding="utf-8") as f:
        f.write(
            """* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background-color: #fff;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

header h1 {
    color: #2c3e50;
    margin-bottom: 10px;
}

.main-content {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
}

.form-container {
    flex: 1;
    min-width: 300px;
    background-color: #fff;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.result-container {
    flex: 1;
    min-width: 300px;
    background-color: #fff;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 20px;
    max-height: calc(100vh - 40px);
    overflow-y: auto;
}

.section {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.section h2 {
    font-size: 1.2rem;
    color: #2c3e50;
    margin-bottom: 15px;
}

.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
}

input[type="text"],
textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: inherit;
    font-size: 1rem;
}

textarea {
    resize: vertical;
}

.form-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;
}

button {
    padding: 10px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s;
}

.btn-primary {
    background-color: #3498db;
    color: white;
}

.btn-primary:hover {
    background-color: #2980b9;
}

.btn-secondary {
    background-color: #2ecc71;
    color: white;
}

.btn-secondary:hover {
    background-color: #27ae60;
}

.btn-danger {
    background-color: #e74c3c;
    color: white;
}

.btn-danger:hover {
    background-color: #c0392b;
}

button:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
}

pre {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 4px;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.9rem;
    line-height: 1.4;
}

@media (max-width: 768px) {
    .main-content {
        flex-direction: column;
    }
    
    .result-container {
        position: static;
        max-height: none;
    }
}"""
        )

    # 创建JavaScript脚本
    with open("static/script.js", "w", encoding="utf-8") as f:
        f.write(
            """document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('langGptForm');
    const resultElement = document.getElementById('result');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 收集表单数据
        const formData = {
            role: document.getElementById('role').value,
            profile: {
                author: document.getElementById('author').value,
                version: document.getElementById('version').value,
                language: document.getElementById('language').value,
                description: document.getElementById('description').value
            },
            skills: document.getElementById('skills').value.split('\\n').filter(skill => skill.trim() !== ''),
            background: document.getElementById('background').value,
            goals: document.getElementById('goals').value.split('\\n').filter(goal => goal.trim() !== ''),
            outputFormat: document.getElementById('outputFormat').value,
            rules: document.getElementById('rules').value.split('\\n').filter(rule => rule.trim() !== ''),
            workflows: document.getElementById('workflows').value.split('\\n').filter(workflow => workflow.trim() !== ''),
            commands: {
                prefix: document.getElementById('commandPrefix').value,
                commands: {}
            },
            initialization: document.getElementById('initialization').value
        };
        
        // 处理命令
        const commandsText = document.getElementById('commands').value;
        if (commandsText.trim() !== '') {
            const commandLines = commandsText.split('\\n');
            for (const line of commandLines) {
                if (line.trim() === '') continue;
                const [name, description] = line.split(':', 2);
                if (name && description) {
                    formData.commands.commands[name.trim()] = description.trim();
                }
            }
        }
        
        // 发送到服务器生成提示词
        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            resultElement.textContent = data.prompt;
            copyBtn.disabled = false;
            downloadBtn.disabled = false;
        })
        .catch(error => {
            console.error('Error:', error);
            resultElement.textContent = '生成提示词时出错: ' + error.message;
        });
    });
    
    // 复制到剪贴板
    copyBtn.addEventListener('click', function() {
        navigator.clipboard.writeText(resultElement.textContent)
            .then(() => {
                alert('提示词已复制到剪贴板！');
            })
            .catch(err => {
                console.error('无法复制: ', err);
                alert('复制失败，请手动复制。');
            });
    });
    
    // 下载为文件
    downloadBtn.addEventListener('click', function() {
        const roleName = document.getElementById('role').value.replace(/\\s+/g, '_').toLowerCase();
        const filename = roleName + '_prompt.md';
        
        fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: filename,
                content: resultElement.textContent
            })
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('下载失败: ' + error.message);
        });
    });
});"""
        )

    return "模板创建成功！"


# 生成提示词
@app.route("/generate", methods=["POST"])
def generate_prompt():
    data = request.json

    prompt = f"# Role: {data['role']}\n\n"

    # 配置文件
    prompt += "## Profile\n"
    prompt += f"- author: {data['profile']['author']}\n"
    prompt += f"- version: {data['profile']['version']}\n"
    prompt += f"- language: {data['profile']['language']}\n"
    prompt += f"- description: {data['profile']['description']}\n\n"

    # 技能
    if data["skills"]:
        prompt += "## Skills\n"
        for skill in data["skills"]:
            prompt += f"- {skill}\n"
        prompt += "\n"

    # 背景信息
    if data["background"]:
        prompt += "## Background\n"
        prompt += f"{data['background']}\n\n"

    # 目标
    if data["goals"]:
        prompt += "## Goals\n"
        for goal in data["goals"]:
            prompt += f"- {goal}\n"
        prompt += "\n"

    # 输出格式
    if data["outputFormat"]:
        prompt += "## OutputFormat\n"
        prompt += f"{data['outputFormat']}\n\n"

    # 规则
    if data["rules"]:
        prompt += "## Rules\n"
        for i, rule in enumerate(data["rules"], 1):
            prompt += f"{i}. {rule}\n"
        prompt += "\n"

    # 工作流程
    if data["workflows"]:
        prompt += "## Workflows\n"
        for i, workflow in enumerate(data["workflows"], 1):
            prompt += f"{i}. {workflow}\n"
        prompt += "\n"

    # 命令
    if data["commands"]["commands"]:
        prompt += "## Commands\n"
        prompt += f"- Prefix: \"{data['commands']['prefix']}\"\n"
        prompt += "- Commands:\n"
        for cmd_name, cmd_desc in data["commands"]["commands"].items():
            prompt += f"    - {cmd_name}: {cmd_desc}\n"
        prompt += "\n"

    # 初始化
    if data["initialization"]:
        prompt += "## Initialization\n"
        prompt += f"{data['initialization']}\n"

    return jsonify({"prompt": prompt})


# 下载文件
@app.route("/download", methods=["POST"])
def download_file():
    data = request.json
    filename = data["filename"]
    content = data["content"]

    # 确保下载目录存在
    os.makedirs("downloads", exist_ok=True)

    # 保存文件
    file_path = os.path.join("downloads", filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return send_from_directory("downloads", filename, as_attachment=True)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # 首次运行时创建模板
    create_templates()
    print("LangGPT提示词生成器Web应用已启动！")
    print("请访问 http://localhost:5000 使用该工具")
    app.run(debug=True)
