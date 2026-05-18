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
WebSearchSkill — Encapsulates web search, browser simulation, and content
extraction capabilities into a pluggable skill.

This skill wraps SearchToolkit and optionally BrowserToolkit, providing:
- DuckDuckGo and Wikipedia search
- Browser-based page interaction
- Document content extraction from URLs

The system prompt fragment is extracted from the original run.py web agent
definition to maintain behavioral parity.
"""

from typing import List

from camel.toolkits import (
    BrowserToolkit,
    FunctionTool,
    SearchToolkit,
)

from owl.utils import DocumentProcessingToolkit

from .base import Skill


class WebSearchSkill(Skill):
    """Skill for web searching, browsing, and content extraction.

    Args:
        model: Model for the document processing toolkit.
        browsing_model: Optional model for the BrowserToolkit web agent.
        planning_model: Optional model for the BrowserToolkit planning agent.
        headless: Whether to run browser in headless mode.
        enable_browser: Whether to include browser simulation tools.
    """

    def __init__(
        self,
        model=None,
        browsing_model=None,
        planning_model=None,
        headless: bool = False,
        enable_browser: bool = True,
    ) -> None:
        self._model = model
        self._browsing_model = browsing_model
        self._planning_model = planning_model
        self._headless = headless
        self._enable_browser = enable_browser

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "A skill for searching the web, extracting webpage content, "
            "simulating browser actions, and retrieving relevant information."
        )

    @property
    def system_prompt_fragment(self) -> str:
        return """You can search the web, extract webpage content, simulate browser actions, and provide relevant information to solve tasks.
Keep in mind that:
- Do not be overly confident in your own knowledge. Searching can provide a broader perspective and help validate existing knowledge.
- If one way fails to provide an answer, try other ways or methods. The answer does exist.
- If the search snippet is unhelpful but the URL comes from an authoritative source, try visit the website for more details.
- When looking for specific numerical values (e.g., dollar amounts), prioritize reliable sources and avoid relying only on search snippets.
- When solving tasks that require web searches, check Wikipedia first before exploring other websites.
- You can also simulate browser actions to get more information or verify the information you have found.
- Browser simulation is also helpful for finding target URLs.
- Do not solely rely on document tools or browser simulation to find the answer, you should combine document tools and browser simulation to comprehensively process web page information.
- In your response, you should mention the urls you have visited and processed.

Tips for web search:
- Never add too many keywords in your search query!
- If the question is complex, the search query should be concise and focus on finding official sources rather than direct answers.
- The results you return do not have to directly answer the original question, you only need to collect relevant information."""

    def get_tools(self) -> List[FunctionTool]:
        tools: List[FunctionTool] = []

        search_toolkit = SearchToolkit()
        tools.append(FunctionTool(search_toolkit.search_duckduckgo))
        tools.append(FunctionTool(search_toolkit.search_wiki))

        if self._model is not None:
            doc_toolkit = DocumentProcessingToolkit(model=self._model)
            tools.append(FunctionTool(doc_toolkit.extract_document_content))

        if self._enable_browser and self._browsing_model and self._planning_model:
            browser_toolkit = BrowserToolkit(
                headless=self._headless,
                web_agent_model=self._browsing_model,
                planning_agent_model=self._planning_model,
            )
            tools.extend(browser_toolkit.get_tools())

        return tools
