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


def document_summarizer_tool(text: str) -> str:
    """Summarize a large document or piece of text.
    
    Args:
        text: The text to summarize.
        
    Returns:
        A concise summary of the text.
    """
    # Note: For demonstration purposes, returning a simple truncation.
    # A real implementation might chain to another LLM call or a local summarizer.
    words = text.split()
    if len(words) > 50:
        return "Summary (mocked): " + " ".join(words[:40]) + "..."
    return text


class DocumentSummarizerSkill(Skill):
    """Provides the capability to summarize large documents."""

    @property
    def name(self) -> str:
        return "document_summarizer"

    @property
    def description(self) -> str:
        return "Summarizes large documents or chunks of text."

    @property
    def system_prompt_fragment(self) -> str:
        return (
            "You have access to a document summarization tool. "
            "Use it when you need to condense large texts into actionable insights."
        )

    def get_tools(self) -> List[FunctionTool]:
        return [FunctionTool(document_summarizer_tool)]
