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

"""
SummarizerSkill — Document processing, image analysis, and file interaction
packaged as a pluggable skill.

This skill wraps DocumentProcessingToolkit, ImageAnalysisToolkit,
CodeExecutionToolkit, and FileToolkit into a composable unit that can
be attached to any agent via the SkillRegistry.
"""

from typing import List

from camel.toolkits import (
    CodeExecutionToolkit,
    FileToolkit,
    FunctionTool,
    ImageAnalysisToolkit,
)

from owl.utils import DocumentProcessingToolkit

from .base import Skill


class SummarizerSkill(Skill):
    """Skill for document processing, image analysis, and summarization.

    Args:
        model: Model for the document processing and image analysis toolkits.
        enable_code_execution: Whether to include code execution tools.
        enable_image_analysis: Whether to include image analysis tools.
    """

    def __init__(
        self,
        model=None,
        enable_code_execution: bool = True,
        enable_image_analysis: bool = True,
    ) -> None:
        self._model = model
        self._enable_code_execution = enable_code_execution
        self._enable_image_analysis = enable_image_analysis

    @property
    def name(self) -> str:
        return "summarizer"

    @property
    def description(self) -> str:
        return (
            "A skill for processing documents (PDF, DOCX, etc.), analyzing "
            "images, executing code, and interacting with the file system."
        )

    @property
    def system_prompt_fragment(self) -> str:
        return """You can process documents and multimodal data, and interact with the file system.
Your capabilities include:
- Extracting content from various document formats (PDF, DOCX, TXT, etc.)
- Analyzing images and answering questions about visual content
- Executing Python code to process and transform data
- Reading and writing files on the local file system
- Processing Excel/CSV files programmatically

When processing documents:
- Extract key information systematically
- Summarize long documents concisely while preserving critical details
- Cross-reference information from multiple sources when available
- If code execution is needed, write and run the code directly"""

    def get_tools(self) -> List[FunctionTool]:
        tools: List[FunctionTool] = []

        if self._model is not None:
            doc_toolkit = DocumentProcessingToolkit(model=self._model)
            tools.append(FunctionTool(doc_toolkit.extract_document_content))

            if self._enable_image_analysis:
                image_toolkit = ImageAnalysisToolkit(model=self._model)
                tools.append(FunctionTool(image_toolkit.ask_question_about_image))

        if self._enable_code_execution:
            code_toolkit = CodeExecutionToolkit(sandbox="subprocess", verbose=True)
            tools.append(FunctionTool(code_toolkit.execute_code))

        file_toolkit = FileToolkit()
        tools.extend(file_toolkit.get_tools())

        return tools
