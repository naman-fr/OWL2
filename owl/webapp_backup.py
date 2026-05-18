# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Import from the correct module path
import importlib
import os
from typing import Dict, List, Tuple

import gradio as gr
from dotenv import find_dotenv, load_dotenv, set_key, unset_key
from utils import run_society

os.environ["PYTHONIOENCODING"] = "utf-8"

# Enhanced CSS with navigation bar and additional styling
custom_css = """
:root {
    --primary-color: #4a89dc;
    --secondary-color: #5d9cec;
    --accent-color: #7baaf7;
    --light-bg: #f8f9fa;
    --border-color: #e4e9f0;
    --text-muted: #8a9aae;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 30px;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    color: white;
    border-radius: 10px 10px 0 0;
    margin-bottom: 0;
    box-shadow: 0 2px 10px rgba(74, 137, 220, 0.15);
}

.navbar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.5em;
    font-weight: bold;
}

.navbar-menu {
    display: flex;
    gap: 20px;
}

/* Navbar styles moved to a more specific section below */

.header {
    text-align: center;
    margin-bottom: 20px;
    background: linear-gradient(180deg, var(--secondary-color), var(--accent-color));
    color: white;
    padding: 40px 20px;
    border-radius: 0 0 10px 10px;
    box-shadow: 0 4px 6px rgba(93, 156, 236, 0.12);
}

.module-info {
    background-color: var(--light-bg);
    border-left: 5px solid var(--primary-color);
    padding: 10px 15px;
    margin-top: 10px;
    border-radius: 5px;
    font-size: 0.9em;
}

.answer-box {
    background-color: var(--light-bg);
    border-left: 5px solid var(--secondary-color);
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.token-count {
    background-color: #e9ecef;
    padding: 10px;
    border-radius: 5px;
    text-align: center;
    font-weight: bold;
    margin-bottom: 20px;
}

.chat-container {
    border: 1px solid var(--border-color);
    border-radius: 5px;
    max-height: 500px;
    overflow-y: auto;
    margin-bottom: 20px;
}

.footer {
    text-align: center;
    margin-top: 20px;
    color: var(--text-muted);
    font-size: 0.9em;
    padding: 20px;
    border-top: 1px solid var(--border-color);
}

.features-section {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin: 20px 0;
}

@media (max-width: 1200px) {
    .features-section {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .features-section {
        grid-template-columns: 1fr;
    }
}

.feature-card {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(74, 137, 220, 0.08);
    transition: transform 0.3s, box-shadow 0.3s;
    height: 100%;
    display: flex;
    flex-direction: column;
    border: 1px solid rgba(228, 233, 240, 0.6);
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(74, 137, 220, 0.15);
    border-color: rgba(93, 156, 236, 0.3);
}

.feature-icon {
    font-size: 2em;
    color: var(--primary-color);
    margin-bottom: 10px;
    text-shadow: 0 1px 2px rgba(74, 137, 220, 0.1);
}

.feature-card h3 {
    margin-top: 10px;
    margin-bottom: 10px;
}

.feature-card p {
    flex-grow: 1;
    font-size: 0.95em;
    line-height: 1.5;
}

/* Navbar link styles - ensuring consistent colors */
.navbar-menu a {
    color: #ffffff !important;
    text-decoration: none;
    padding: 5px 10px;
    border-radius: 5px;
    transition: background-color 0.3s, color 0.3s;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.navbar-menu a:hover {
    background-color: rgba(255, 255, 255, 0.15);
    color: #ffffff !important;
}

/* Improved button and input styles */
button.primary {
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    transition: all 0.3s;
}

button.primary:hover {
    background: linear-gradient(90deg, var(--secondary-color), var(--primary-color));
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.env-section {
    background-color: var(--light-bg);
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.env-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}

.env-table th, .env-table td {
    padding: 10px;
    border: 1px solid var(--border-color);
}

.env-table th {
    background-color: var(--primary-color);
    color: white;
    text-align: left;
}

.env-table tr:nth-child(even) {
    background-color: rgba(0, 0, 0, 0.02);
}

.env-actions {
    display: flex;
    gap: 10px;
}

.env-var-input {
    margin-bottom: 15px;
}

.env-save-status {
    margin-top: 15px;
    padding: 10px;
    border-radius: 5px;
}

.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}
"""

# Dictionary containing module descriptions
MODULE_DESCRIPTIONS = {
    "run": "默认模式：使用OpenAI模型的默认的智能体协作模式，适合大多数任务。",
    "run_mini": "使用使用OpenAI模型最小化配置处理任务",
    "run_deepseek_zh": "使用deepseek模型处理中文任务",
    "run_terminal_zh": "终端模式：可执行命令行操作，支持网络搜索、文件处理等功能。适合需要系统交互的任务，使用OpenAI模型",
    "run_gaia_roleplaying": "GAIA基准测试实现，用于评估Agent能力",
    "run_openai_compatible_model": "使用openai兼容模型处理任务",
    "run_ollama": "使用本地ollama模型处理任务",
    "run_qwen_mini_zh": "使用qwen模型最小化配置处理任务",
    "run_qwen_zh": "使用qwen模型处理任务",
}

# 默认环境变量模板
DEFAULT_ENV_TEMPLATE = """# MODEL & API (See https://docs.camel-ai.org/key_modules/models.html#)

# OPENAI API
# OPENAI_API_KEY= ""
# OPENAI_API_BASE_URL=""

# Qwen API (https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key)
# QWEN_API_KEY=""

# DeepSeek API (https://platform.deepseek.com/api_keys)
# DEEPSEEK_API_KEY=""

#===========================================
# Tools & Services API
#===========================================

# Google Search API (https://developers.google.com/custom-search/v1/overview)
GOOGLE_API_KEY=""
SEARCH_ENGINE_ID=""

# Hugging Face API (https://huggingface.co/join)
HF_TOKEN=""

# Chunkr API (https://chunkr.ai/)
CHUNKR_API_KEY=""

# Firecrawl API (https://www.firecrawl.dev/)
FIRECRAWL_API_KEY=""
#FIRECRAWL_API_URL="https://api.firecrawl.dev"
"""


def format_chat_history(chat_history: List[Dict[str, str]]) -> List[List[str]]:
    """将聊天历史格式化为Gradio聊天组件可接受的格式

    Args:
        chat_history: 原始聊天历史

    Returns:
        List[List[str]]: 格式化后的聊天历史
    """
    formatted_history = []
    for message in chat_history:
        user_msg = message.get("user", "")
        assistant_msg = message.get("assistant", "")

        if user_msg:
            formatted_history.append([user_msg, None])
        if assistant_msg and formatted_history:
            formatted_history[-1][1] = assistant_msg
        elif assistant_msg:
            formatted_history.append([None, assistant_msg])

    return formatted_history


def validate_input(question: str) -> bool:
    """验证用户输入是否有效

    Args:
        question: 用户问题

    Returns:
        bool: 输入是否有效
    """
    # 检查输入是否为空或只包含空格
    if not question or question.strip() == "":
        return False
    return True


def run_owl(
    question: str, example_module: str
) -> Tuple[str, List[List[str]], str, str]:
    """运行OWL系统并返回结果

    Args:
        question: 用户问题
        example_module: 要导入的示例模块名（如 "run_terminal_zh" 或 "run_deep"）

    Returns:
        Tuple[...]: 回答、聊天历史、令牌计数、状态
    """
    # 验证输入
    if not validate_input(question):
        return ("请输入有效的问题", [], "0", "❌ 错误: 输入无效")

    try:
        # 确保环境变量已加载
        load_dotenv(find_dotenv(), override=True)
        # 检查模块是否在MODULE_DESCRIPTIONS中
        if example_module not in MODULE_DESCRIPTIONS:
            return (
                f"所选模块 '{example_module}' 不受支持",
                [],
                "0",
                "❌ 错误: 不支持的模块",
            )

        # 动态导入目标模块
        module_path = f"owl.examples.{example_module}"
        try:
            module = importlib.import_module(module_path)
        except ImportError as ie:
            return (
                f"无法导入模块: {module_path}",
                [],
                "0",
                f"❌ 错误: 模块 {example_module} 不存在或无法加载 - {str(ie)}",
            )
        except Exception as e:
            return (f"导入模块时发生错误: {module_path}", [], "0", f"❌ 错误: {str(e)}")

        # 检查是否包含construct_society函数
        if not hasattr(module, "construct_society"):
            return (
                f"模块 {module_path} 中未找到 construct_society 函数",
                [],
                "0",
                "❌ 错误: 模块接口不兼容",
            )

        # 构建社会模拟
        try:
            society = module.construct_society(question)
        except Exception as e:
            return (
                f"构建社会模拟时发生错误: {str(e)}",
                [],
                "0",
                f"❌ 错误: 构建失败 - {str(e)}",
            )

        # 运行社会模拟
        try:
            answer, chat_history, token_info = run_society(society)
        except Exception as e:
            return (
                f"运行社会模拟时发生错误: {str(e)}",
                [],
                "0",
                f"❌ 错误: 运行失败 - {str(e)}",
            )

        # 格式化聊天历史
        try:
            formatted_chat_history = format_chat_history(chat_history)
        except Exception:
            # 如果格式化失败，返回空历史记录但继续处理
            formatted_chat_history = []

        # 安全地获取令牌计数
        if not isinstance(token_info, dict):
            token_info = {}

        completion_tokens = token_info.get("completion_token_count", 0)
        prompt_tokens = token_info.get("prompt_token_count", 0)
        total_tokens = completion_tokens + prompt_tokens

        return (
            answer,
            formatted_chat_history,
            f"完成令牌: {completion_tokens:,} | 提示令牌: {prompt_tokens:,} | 总计: {total_tokens:,}",
            "✅ 成功完成",
        )

    except Exception as e:
        return (f"发生错误: {str(e)}", [], "0", f"❌ 错误: {str(e)}")


def update_module_description(module_name: str) -> str:
    """返回所选模块的描述"""
    return MODULE_DESCRIPTIONS.get(module_name, "无可用描述")


# 环境变量管理功能
def init_env_file():
    """初始化.env文件如果不存在"""
    dotenv_path = find_dotenv()
    if not dotenv_path:
        with open(".env", "w") as f:
            f.write(DEFAULT_ENV_TEMPLATE)
        dotenv_path = find_dotenv()
    return dotenv_path


def load_env_vars():
    """加载环境变量并返回字典格式"""
    dotenv_path = init_env_file()
    load_dotenv(dotenv_path, override=True)

    env_vars = {}
    with open(dotenv_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip("\"'")

    return env_vars


def save_env_vars(env_vars):
    """保存环境变量到.env文件"""
    try:
        dotenv_path = init_env_file()

        # 保存每个环境变量
        for key, value in env_vars.items():
            if key and key.strip():  # 确保键不为空
                set_key(dotenv_path, key.strip(), value.strip())

        # 重新加载环境变量以确保生效
        load_dotenv(dotenv_path, override=True)

        return True, "环境变量已成功保存！"
    except Exception as e:
        return False, f"保存环境变量时出错: {str(e)}"


def add_env_var(key, value):
    """添加或更新单个环境变量"""
    try:
        if not key or not key.strip():
            return False, "变量名不能为空"

        dotenv_path = init_env_file()
        set_key(dotenv_path, key.strip(), value.strip())
        load_dotenv(dotenv_path, override=True)

        return True, f"环境变量 {key} 已成功添加/更新！"
    except Exception as e:
        return False, f"添加环境变量时出错: {str(e)}"


def delete_env_var(key):
    """删除环境变量"""
    try:
        if not key or not key.strip():
            return False, "变量名不能为空"

        dotenv_path = init_env_file()
        unset_key(dotenv_path, key.strip())

        # 从当前进程环境中也删除
        if key in os.environ:
            del os.environ[key]

        return True, f"环境变量 {key} 已成功删除！"
    except Exception as e:
        return False, f"删除环境变量时出错: {str(e)}"


def mask_sensitive_value(key: str, value: str) -> str:
    """对敏感信息进行掩码处理

    Args:
        key: 环境变量名
        value: 环境变量值

    Returns:
        str: 处理后的值
    """
    # 定义需要掩码的敏感关键词
    sensitive_keywords = ["key", "token", "secret", "password", "api"]

    # 检查是否包含敏感关键词（不区分大小写）
    is_sensitive = any(keyword in key.lower() for keyword in sensitive_keywords)

    if is_sensitive and value:
        # 如果是敏感信息且有值，则显示掩码
        return "*" * 8
    return value


def update_env_table():
    """更新环境变量表格显示，对敏感信息进行掩码处理"""
    env_vars = load_env_vars()
    # 对敏感值进行掩码处理
    masked_env_vars = [[k, mask_sensitive_value(k, v)] for k, v in env_vars.items()]
    return masked_env_vars


def create_ui():
    """创建增强版Gradio界面"""
    with gr.Blocks(css=custom_css, theme=gr.themes.Soft(primary_hue="blue")) as app:
        with gr.Column(elem_classes="container"):
            gr.HTML("""
                <div class="navbar">
                    <div class="navbar-logo">
                        🦉 OWL 多智能体协作系统
                    </div>
                    <div class="navbar-menu">
                        <a href="#home">首页</a>
                        <a href="#env-settings">环境设置</a>
                        <a href="https://github.com/camel-ai/owl/blob/main/README.md#-community">加入交流群</a>
                        <a href="https://github.com/camel-ai/owl/blob/main/README.md">OWL文档</a>
                        <a href="https://github.com/camel-ai/camel">CAMEL框架</a>
                        <a href="https://camel-ai.org">CAMEL-AI官网</a>
                    </div>
                </div>
                <div class="header" id="home">
                    
                    <p>我们的愿景是彻底改变AI代理协作解决现实世界任务的方式。通过利用动态代理交互，OWL能够在多个领域实现更自然、高效和稳健的任务自动化。</p>
                </div>
            """)

            with gr.Row(elem_id="features"):
                gr.HTML("""
                <div class="features-section">
                    <div class="feature-card">
                        <div class="feature-icon">🔍</div>
                        <h3>实时信息检索</h3>
                        <p>利用维基百科、谷歌搜索和其他在线资源获取最新信息。</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📹</div>
                        <h3>多模态处理</h3>
                        <p>支持处理互联网或本地的视频、图像和音频数据。</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🌐</div>
                        <h3>浏览器自动化</h3>
                        <p>使用Playwright框架模拟浏览器交互，实现网页操作自动化。</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📄</div>
                        <h3>文档解析</h3>
                        <p>从各种文档格式中提取内容，并转换为易于处理的格式。</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">💻</div>
                        <h3>代码执行</h3>
                        <p>使用解释器编写和运行Python代码，实现自动化数据处理。</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🧰</div>
                        <h3>内置工具包</h3>
                        <p>提供丰富的工具包，支持搜索、数据分析、代码执行等多种功能。</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔑</div>
                        <h3>环境变量管理</h3>
                        <p>便捷管理API密钥和环境配置，安全存储敏感信息。</p>
                    </div>
                </div>
            """)

            with gr.Row():
                with gr.Column(scale=2):
                    question_input = gr.Textbox(
                        lines=5,
                        placeholder="请输入您的问题...",
                        label="问题",
                        elem_id="question_input",
                    )

                    # 增强版模块选择下拉菜单
                    # 只包含MODULE_DESCRIPTIONS中定义的模块
                    module_dropdown = gr.Dropdown(
                        choices=list(MODULE_DESCRIPTIONS.keys()),
                        value="run_terminal_zh",
                        label="选择功能模块",
                        interactive=True,
                    )

                    # 模块描述文本框
                    module_description = gr.Textbox(
                        value=MODULE_DESCRIPTIONS["run_terminal_zh"],
                        label="模块描述",
                        interactive=False,
                        elem_classes="module-info",
                    )

                    run_button = gr.Button(
                        "运行", variant="primary", elem_classes="primary"
                    )

                with gr.Column(scale=1):
                    gr.Markdown("""
                    ### 使用指南
                    
                    1. **选择适合的模块**：根据您的任务需求选择合适的功能模块
                    2. **详细描述您的需求**：在输入框中清晰描述您的问题或任务
                    3. **启动智能处理**：点击"运行"按钮开始多智能体协作处理
                    4. **查看结果**：在下方标签页查看回答和完整对话历史
                    
                    > **高级提示**: 对于复杂任务，可以尝试指定具体步骤和预期结果
                    """)

            status_output = gr.Textbox(label="状态", interactive=False)

            with gr.Tabs():
                with gr.TabItem("回答"):
                    answer_output = gr.Textbox(
                        label="回答", lines=10, elem_classes="answer-box"
                    )

                with gr.TabItem("对话历史"):
                    chat_output = gr.Chatbot(
                        label="完整对话记录", elem_classes="chat-container", height=500
                    )

            token_count_output = gr.Textbox(
                label="令牌计数", interactive=False, elem_classes="token-count"
            )

            # 示例问题
            examples = [
                "打开百度搜索，总结一下camel-ai的camel框架的github star、fork数目等，并把数字用plot包写成python文件保存到本地，用本地终端执行python文件显示图出来给我",
                "请分析GitHub上CAMEL-AI项目的最新统计数据。找出该项目的星标数量、贡献者数量和最近的活跃度。",
                "浏览亚马逊并找出一款对程序员有吸引力的产品。请提供产品名称和价格",
                "写一个hello world的python文件，保存到本地",
            ]

            gr.Examples(examples=examples, inputs=question_input)
            # 新增: 环境变量管理选项卡
            with gr.TabItem("环境变量管理", id="env-settings"):
                gr.Markdown("""
                    ## 环境变量管理
                    
                    在此处设置模型API密钥和其他服务凭证。这些信息将保存在本地的`.env`文件中，确保您的API密钥安全存储且不会上传到网络。
                    """)

                # 环境变量表格
                env_table = gr.Dataframe(
                    headers=["变量名", "值"],
                    datatype=["str", "str"],
                    row_count=10,
                    col_count=(2, "fixed"),
                    value=update_env_table,
                    label="当前环境变量",
                    interactive=False,
                )

                with gr.Row():
                    with gr.Column(scale=1):
                        new_env_key = gr.Textbox(
                            label="变量名", placeholder="例如: OPENAI_API_KEY"
                        )
                    with gr.Column(scale=2):
                        new_env_value = gr.Textbox(
                            label="值", placeholder="输入API密钥或其他配置值"
                        )

                with gr.Row():
                    add_env_button = gr.Button("添加/更新变量", variant="primary")
                    refresh_button = gr.Button("刷新变量列表")
                    delete_env_button = gr.Button("删除选定变量", variant="stop")

                env_status = gr.Textbox(label="状态", interactive=False)

                # 变量选择器（用于删除）
                env_var_to_delete = gr.Dropdown(
                    choices=[], label="选择要删除的变量", interactive=True
                )

                # 更新变量选择器的选项
                def update_delete_dropdown():
                    env_vars = load_env_vars()
                    return gr.Dropdown.update(choices=list(env_vars.keys()))

                # 连接事件处理函数
                add_env_button.click(
                    fn=lambda k, v: add_env_var(k, v),
                    inputs=[new_env_key, new_env_value],
                    outputs=[env_status],
                ).then(fn=update_env_table, outputs=[env_table]).then(
                    fn=update_delete_dropdown, outputs=[env_var_to_delete]
                ).then(
                    fn=lambda: ("", ""),  # 修改为返回两个空字符串的元组
                    outputs=[new_env_key, new_env_value],
                )

                refresh_button.click(fn=update_env_table, outputs=[env_table]).then(
                    fn=update_delete_dropdown, outputs=[env_var_to_delete]
                )

                delete_env_button.click(
                    fn=lambda k: delete_env_var(k),
                    inputs=[env_var_to_delete],
                    outputs=[env_status],
                ).then(fn=update_env_table, outputs=[env_table]).then(
                    fn=update_delete_dropdown, outputs=[env_var_to_delete]
                )

            gr.HTML("""
                <div class="footer" id="about">
                    <h3>关于 OWL 多智能体协作系统</h3>
                    <p>OWL 是一个基于CAMEL框架开发的先进多智能体协作系统，旨在通过智能体协作解决复杂问题。</p>
                    <p>© 2025 CAMEL-AI.org. 基于Apache License 2.0开源协议</p>
                    <p><a href="https://github.com/camel-ai/owl" target="_blank">GitHub</a></p>
                </div>
            """)

            # 设置事件处理
            run_button.click(
                fn=run_owl,
                inputs=[question_input, module_dropdown],
                outputs=[answer_output, chat_output, token_count_output, status_output],
            )

            # 模块选择更新描述
            module_dropdown.change(
                fn=update_module_description,
                inputs=module_dropdown,
                outputs=module_description,
            )

    return app


# 主函数
def main():
    try:
        # 初始化.env文件（如果不存在）
        init_env_file()
        app = create_ui()
        app.launch(share=False)
    except Exception as e:
        print(f"启动应用程序时发生错误: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
