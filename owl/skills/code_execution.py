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

from typing import List

from camel.toolkits import FunctionTool

from .base import Skill


def execute_python_code(code: str) -> str:
    """Execute Python code and return the output.
    
    Args:
        code: The Python code to execute.
        
    Returns:
        The standard output or error message from the execution.
    """
    # Note: For demonstration purposes. In production use E2B or a secure sandbox.
    import sys
    import io
    import os
    
    # Track files before execution
    try:
        before_files = set(os.listdir("."))
    except Exception:
        before_files = set()
        
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        # Use a restricted globals dict
        exec(code, {"__builtins__": __builtins__}, {})
        output = sys.stdout.getvalue()
    except Exception as e:
        output = f"Error: {e}"
    finally:
        sys.stdout = original_stdout
        
    # Track files after execution
    try:
        after_files = set(os.listdir("."))
        new_files = after_files - before_files
        if new_files:
            output += f"\n[Execution completed. Generated new files: {', '.join(new_files)}]"
    except Exception:
        pass
        
    return output


class CodeExecutionSkill(Skill):
    """Provides the capability to execute Python code snippets."""

    @property
    def name(self) -> str:
        return "code_execution"

    @property
    def description(self) -> str:
        return "Executes Python code and returns the standard output."

    @property
    def system_prompt_fragment(self) -> str:
        return (
            "You have access to a Python code execution environment. "
            "Use it to perform mathematical calculations, run scripts, "
            "or verify logical steps. Always print your results to see them."
        )

    def get_tools(self) -> List[FunctionTool]:
        return [FunctionTool(execute_python_code)]
