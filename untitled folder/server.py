from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from flask import Flask, render_template, request, jsonify
import os
import json
from main import LangGPTPromptGenerator

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json

    generator = LangGPTPromptGenerator()

    # 设置角色和配置文件
    generator.set_role(data.get("role", ""))
    generator.set_profile(
        author=data.get("author", ""),
        version=data.get("version", "1.0"),
        language=data.get("language", "中文"),
        description=data.get("description", ""),
    )

    # 添加技能
    skills = data.get("skills", [])
    if skills:
        generator.add_skills(skills)

    # 设置背景
    background = data.get("background", "")
    if background:
        generator.set_background(background)

    # 添加目标
    goals = data.get("goals", [])
    if goals:
        generator.add_goals(goals)

    # 设置输出格式
    output_format = data.get("output_format", "")
    if output_format:
        generator.set_output_format(output_format)

    # 添加规则
    rules = data.get("rules", [])
    if rules:
        generator.add_rules(rules)

    # 添加工作流程
    workflows = data.get("workflows", [])
    if workflows:
        generator.add_workflows(workflows)

    # 添加命令
    commands = data.get("commands", {})
    if commands:
        generator.add_commands(commands)

    # 设置初始化文本
    init = data.get("init", "")
    if init:
        generator.set_init(init)

    # 生成prompt
    prompt = generator.generate_prompt()

    return jsonify({"prompt": prompt})


@app.route("/save", methods=["POST"])
def save():
    data = request.json
    prompt = data.get("prompt", "")
    filename = data.get("filename", "langgpt_prompt.txt")

    if not filename.endswith(".txt"):
        filename += ".txt"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(prompt)
        return jsonify({"success": True, "message": f"Prompt已保存到 {filename}"})
    except Exception as e:
        return jsonify({"success": False, "message": f"保存失败: {str(e)}"})


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")

    # 确保templates目录存在
    if not os.path.exists("templates"):
        os.makedirs("templates")

    # 创建index.html文件
    index_html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGPT Prompt生成助手</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 20px;
            padding-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .list-input-container {
            margin-bottom: 10px;
        }
        .list-item {
            display: flex;
            margin-bottom: 5px;
        }
        .list-item input {
            flex-grow: 1;
            margin-right: 5px;
        }
        .prompt-result {
            white-space: pre-wrap;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4">LangGPT Prompt生成助手</h1>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <ul class="nav nav-tabs card-header-tabs" id="formTabs" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="basic-tab" data-bs-toggle="tab" data-bs-target="#basic" type="button" role="tab" aria-controls="basic" aria-selected="true">基本信息</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="skills-tab" data-bs-toggle="tab" data-bs-target="#skills" type="button" role="tab" aria-controls="skills" aria-selected="false">技能</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="background-tab" data-bs-toggle="tab" data-bs-target="#background" type="button" role="tab" aria-controls="background" aria-selected="false">背景</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="goals-tab" data-bs-toggle="tab" data-bs-target="#goals" type="button" role="tab" aria-controls="goals" aria-selected="false">目标</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="rules-tab" data-bs-toggle="tab" data-bs-target="#rules" type="button" role="tab" aria-controls="rules" aria-selected="false">规则</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="workflows-tab" data-bs-toggle="tab" data-bs-target="#workflows" type="button" role="tab" aria-controls="workflows" aria-selected="false">工作流</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="commands-tab" data-bs-toggle="tab" data-bs-target="#commands" type="button" role="tab" aria-controls="commands" aria-selected="false">命令</button>
                            </li>
                        </ul>
                    </div>
                    <div class="card-body">
                        <div class="tab-content" id="formTabsContent">
                            <!-- 基本信息 -->
                            <div class="tab-pane fade show active" id="basic" role="tabpanel" aria-labelledby="basic-tab">
                                <div class="form-group">
                                    <label for="role">角色名称 *</label>
                                    <input type="text" class="form-control" id="role" placeholder="例如：编程导师">
                                </div>
                                <div class="form-group">
                                    <label for="author">作者 *</label>
                                    <input type="text" class="form-control" id="author" placeholder="例如：用户">
                                </div>
                                <div class="form-group">
                                    <label for="version">版本</label>
                                    <input type="text" class="form-control" id="version" placeholder="例如：1.0" value="1.0">
                                </div>
                                <div class="form-group">
                                    <label for="language">语言</label>
                                    <input type="text" class="form-control" id="language" placeholder="例如：中文" value="中文">
                                </div>
                                <div class="form-group">
                                    <label for="description">描述 *</label>
                                    <textarea class="form-control" id="description" rows="3" placeholder="例如：你是一位经验丰富的编程导师，专注于帮助初学者学习编程基础和解决编程问题。"></textarea>
                                </div>
                                <div class="form-group">
                                    <label for="output_format">输出格式</label>
                                    <textarea class="form-control" id="output_format" rows="3" placeholder="例如：回答应该包含清晰的解释和相关的代码示例，代码应该有注释说明。"></textarea>
                                </div>
                            </div>
                            
                            <!-- 技能 -->
                            <div class="tab-pane fade" id="skills" role="tabpanel" aria-labelledby="skills-tab">
                                <div class="list-input-container" id="skills-container">
                                    <div class="list-item">
                                        <input type="text" class="form-control" placeholder="例如：精通多种编程语言，包括Python、JavaScript和Java">
                                        <button type="button" class="btn btn-danger btn-sm remove-item">删除</button>
                                    </div>
                                </div>
                                <button type="button" class="btn btn-primary btn-sm" id="add-skill">添加技能</button>
                            </div>
                            
                            <!-- 背景 -->
                            <div class="tab-pane fade" id="background" role="tabpanel" aria-labelledby="background-tab">
                                <div class="form-group">
                                    <label for="background-text">背景信息</label>
                                    <textarea class="form-control" id="background-text" rows="5" placeholder="例如：我有10年的软件开发经验和5年的教学经验，擅长将复杂概念简化为易于理解的部分。"></textarea>
                                </div>
                            </div>
                            
                            <!-- 目标 -->
                            <div class="tab-pane fade" id="goals" role="tabpanel" aria-labelledby="goals-tab">
                                <div class="list-input-container" id="goals-container">
                                    <div class="list-item">
                                        <input type="text" class="form-control" placeholder="例如：帮助用户理解编程概念">
                                        <button type="button" class="btn btn-danger btn-sm remove-item">删除</button>
                                    </div>
                                </div>
                                <button type="button" class="btn btn-primary btn-sm" id="add-goal">添加目标</button>
                            </div>
                            
                            <!-- 规则 -->
                            <div class="tab-pane fade" id="rules" role="tabpanel" aria-labelledby="rules-tab">
                                <div class="list-input-container" id="rules-container">
                                    <div class="list-item">
                                        <input type="text" class="form-control" placeholder="例如：始终保持耐心和鼓励的态度">
                                        <button type="button" class="btn btn-danger btn-sm remove-item">删除</button>
                                    </div>
                                </div>
                                <button type="button" class="btn btn-primary btn-sm" id="add-rule">添加规则</button>
                            </div>
                            
                            <!-- 工作流 -->
                            <div class="tab-pane fade" id="workflows" role="tabpanel" aria-labelledby="workflows-tab">
                                <div class="list-input-container" id="workflows-container">
                                    <div class="list-item">
                                        <input type="text" class="form-control" placeholder="例如：首先理解用户的问题或需求">
                                        <button type="button" class="btn btn-danger btn-sm remove-item">删除</button>
                                    </div>
                                </div>
                                <button type="button" class="btn btn-primary btn-sm" id="add-workflow">添加工作流</button>
                            </div>
                            
                            <!-- 命令 -->
                            <div class="tab-pane fade" id="commands" role="tabpanel" aria-labelledby="commands-tab">
                                <div class="form-group">
                                    <label for="command-prefix">命令前缀</label>
                                    <input type="text" class="form-control" id="command-prefix" placeholder="例如：/" value="/">
                                </div>
                                <div class="list-input-container" id="commands-container">
                                    <div class="list-item">
                                        <input type="text" class="form-control command-key" placeholder="命令名称，例如：help">
                                        <input type="text" class="form-control command-value" placeholder="命令描述，例如：显示帮助信息">
                                        <button type="button" class="btn btn-danger btn-sm remove-item">删除</button>
                                    </div>
                                </div>
                                <button type="button" class="btn btn-primary btn-sm" id="add-command">添加命令</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="form-group mt-3">
                    <label for="init">初始化文本</label>
                    <textarea class="form-control" id="init" rows="3" placeholder="例如：作为一个<Role>，你必须遵循<Rules>，你必须使用默认的<Language>与用户交流，你必须向用户问好。然后介绍自己并介绍<Workflow>。"></textarea>
                </div>
                
                <div class="d-grid gap-2 mt-3">
                    <button type="button" class="btn btn-primary" id="generate-btn">生成Prompt</button>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">生成的Prompt</h5>
                            <div>
                                <button type="button" class="btn btn-sm btn-outline-primary" id="copy-btn">复制</button>
                                <button type="button" class="btn btn-sm btn-outline-success" id="save-btn">保存</button>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="prompt-result" id="prompt-result">
                            <p class="text-muted">点击"生成Prompt"按钮生成LangGPT格式的prompt</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 保存对话框 -->
    <div class="modal fade" id="saveModal" tabindex="-1" aria-labelledby="saveModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="saveModalLabel">保存Prompt</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label for="filename">文件名</label>
                        <input type="text" class="form-control" id="filename" placeholder="例如：my_prompt.txt" value="langgpt_prompt.txt">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                    <button type="button" class="btn btn-primary" id="confirm-save-btn">保存</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // 添加列表项
            function addListItem(containerId, placeholder) {
                const container = document.getElementById(containerId);
                const item = document.createElement('div');
                item.className = 'list-item';
                
                if (containerId === 'commands-container') {
                    item.innerHTML = `
                        <input type="text" class="form-control command-key" placeholder="命令名称，例如：help">
                        <input type="text" class="form-control command-value" placeholder="命令描述，例如：显示帮助信息">
                        <button type="button" class="btn btn-danger btn-sm remove-item">删除</button>
                    `;
                } else {
                    item.innerHTML = `
                        <input type="text" class="form-control" placeholder="${placeholder}">
                        <button type="button" class="btn btn-danger btn-sm remove-item">删除</button>
                    `;
                }
                
                container.appendChild(item);
                
                // 添加删除按钮事件
                item.querySelector('.remove-item').addEventListener('click', function() {
                    container.removeChild(item);
                });
            }
            
            // 添加按钮事件
            document.getElementById('add-skill').addEventListener('click', function() {
                addListItem('skills-container', '例如：精通多种编程语言，包括Python、JavaScript和Java');
            });
            
            document.getElementById('add-goal').addEventListener('click', function() {
                addListItem('goals-container', '例如：帮助用户理解编程概念');
            });
            
            document.getElementById('add-rule').addEventListener('click', function() {
                addListItem('rules-container', '例如：始终保持耐心和鼓励的态度');
            });
            
            document.getElementById('add-workflow').addEventListener('click', function() {
                addListItem('workflows-container', '例如：首先理解用户的问题或需求');
            });
            
            document.getElementById('add-command').addEventListener('click', function() {
                addListItem('commands-container', '');
            });
            
            // 删除按钮事件
            document.querySelectorAll('.remove-item').forEach(button => {
                button.addEventListener('click', function() {
                    const item = this.parentElement;
                    const container = item.parentElement;
                    container.removeChild(item);
                });
            });
            
            // 生成Prompt
            document.getElementById('generate-btn').addEventListener('click', function() {
                // 收集基本信息
                const role = document.getElementById('role').value;
                const author = document.getElementById('author').value;
                const version = document.getElementById('version').value;
                const language = document.getElementById('language').value;
                const description = document.getElementById('description').value;
                const outputFormat = document.getElementById('output_format').value;
                const background = document.getElementById('background-text').value;
                const init = document.getElementById('init').value;
                
                // 验证必填字段
                if (!role || !author || !description) {
                    alert('请填写必填字段：角色名称、作者和描述');
                    return;
                }
                
                // 收集技能
                const skills = [];
                document.querySelectorAll('#skills-container .list-item input').forEach(input => {
                    if (input.value.trim()) {
                        skills.push(input.value.trim());
                    }
                });
                
                // 收集目标
                const goals = [];
                document.querySelectorAll('#goals-container .list-item input').forEach(input => {
                    if (input.value.trim()) {
                        goals.push(input.value.trim());
                    }
                });
                
                // 收集规则
                const rules = [];
                document.querySelectorAll('#rules-container .list-item input').forEach(input => {
                    if (input.value.trim()) {
                        rules.push(input.value.trim());
                    }
                });
                
                // 收集工作流程
                const workflows = [];
                document.querySelectorAll('#workflows-container .list-item input').forEach(input => {
                    if (input.value.trim()) {
                        workflows.push(input.value.trim());
                    }
                });
                
                // 收集命令
                const commandPrefix = document.getElementById('command-prefix').value;
                const commands = {};
                const commandItems = document.querySelectorAll('#commands-container .list-item');
                commandItems.forEach(item => {
                    const key = item.querySelector('.command-key').value.trim();
                    const value = item.querySelector('.command-value').value.trim();
                    if (key && value) {
                        commands[key] = value;
                    }
                });
                
                // 准备数据
                const data = {
                    role: role,
                    author: author,
                    version: version,
                    language: language,
                    description: description,
                    skills: skills,
                    background: background,
                    goals: goals,
                    output_format: outputFormat,
                    rules: rules,
                    workflows: workflows,
                    commands: commands,
                    command_prefix: commandPrefix,
                    init: init
                };
                
                // 发送请求
                fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('prompt-result').textContent = data.prompt;
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('生成Prompt时出错');
                });
            });
            
            // 复制按钮
            document.getElementById('copy-btn').addEventListener('click', function() {
                const promptText = document.getElementById('prompt-result').textContent;
                navigator.clipboard.writeText(promptText)
                    .then(() => {
                        alert('Prompt已复制到剪贴板');
                    })
                    .catch(err => {
                        console.error('复制失败:', err);
                        alert('复制失败');
                    });
            });
            
            // 保存按钮
            document.getElementById('save-btn').addEventListener('click', function() {
                const promptText = document.getElementById('prompt-result').textContent;
                if (!promptText || promptText.includes('点击"生成Prompt"按钮生成LangGPT格式的prompt')) {
                    alert('请先生成Prompt');
                    return;
                }
                
                // 显示保存对话框
                const saveModal = new bootstrap.Modal(document.getElementById('saveModal'));
                saveModal.show();
            });
            
            // 确认保存
            document.getElementById('confirm-save-btn').addEventListener('click', function() {
                const promptText = document.getElementById('prompt-result').textContent;
                const filename = document.getElementById('filename').value;
                
                fetch('/save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        prompt: promptText,
                        filename: filename
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        // 关闭对话框
                        const saveModal = bootstrap.Modal.getInstance(document.getElementById('saveModal'));
                        saveModal.hide();
                    } else {
                        alert(data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('保存Prompt时出错');
                });
            });
        });
    </script>
</body>
</html>
    """

    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    app.run(debug=True, host="0.0.0.0", port=5000)
