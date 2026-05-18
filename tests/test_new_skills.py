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

from owl.skills.code_execution import CodeExecutionSkill, execute_python_code
from owl.skills.document_summarizer import DocumentSummarizerSkill, document_summarizer_tool


def test_code_execution_skill_properties():
    skill = CodeExecutionSkill()
    assert skill.name == "code_execution"
    assert "Executes Python code" in skill.description
    assert "Python code execution environment" in skill.system_prompt_fragment

    tools = skill.get_tools()
    assert len(tools) == 1
    assert tools[0].func == execute_python_code

def test_execute_python_code_success():
    code = "print('Hello, ' + 'World!')\nprint(2 + 2)"
    output = execute_python_code(code)
    assert "Hello, World!" in output
    assert "4" in output

def test_execute_python_code_error():
    code = "1 / 0"
    output = execute_python_code(code)
    assert "Error: division by zero" in output

def test_document_summarizer_skill_properties():
    skill = DocumentSummarizerSkill()
    assert skill.name == "document_summarizer"
    assert "Summarizes large documents" in skill.description
    assert "document summarization tool" in skill.system_prompt_fragment

    tools = skill.get_tools()
    assert len(tools) == 1
    assert tools[0].func == document_summarizer_tool

def test_document_summarizer_tool_short():
    text = "This is a short text."
    output = document_summarizer_tool(text)
    assert output == text

def test_document_summarizer_tool_long():
    text = "word " * 60
    output = document_summarizer_tool(text)
    assert "Summary" in output
    assert "..." in output
