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
Skill — Abstract base class for pluggable agent capabilities.

A Skill encapsulates a coherent set of tools and a system prompt fragment
that can be composed onto a ChatAgent without modifying agent construction
code.  New skills can be added by subclassing :class:`Skill` and registering
with the :class:`SkillRegistry`.

Example::

    class MyCustomSkill(Skill):
        @property
        def name(self) -> str:
            return "my_custom_skill"

        @property
        def description(self) -> str:
            return "Does something custom."

        @property
        def system_prompt_fragment(self) -> str:
            return "You can do custom things."

        def get_tools(self) -> List[FunctionTool]:
            return [FunctionTool(my_function)]
"""

from abc import ABC, abstractmethod
from typing import List

from camel.toolkits import FunctionTool


class Skill(ABC):
    """Abstract base class for a pluggable agent skill.

    Subclass this to define a new skill.  Each skill provides:
    - A unique name
    - A human-readable description (used for worker registration)
    - A system prompt fragment that is appended to the agent's system message
    - A list of FunctionTools that the agent can invoke
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this skill (e.g., ``'web_search'``)."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this skill does."""
        ...

    @property
    @abstractmethod
    def system_prompt_fragment(self) -> str:
        """System prompt text to be appended to the agent's instructions.

        This should describe the skill's capabilities and usage tips
        without duplicating the core agent identity.
        """
        ...

    @abstractmethod
    def get_tools(self) -> List[FunctionTool]:
        """Return the list of tools provided by this skill.

        Returns:
            A list of :class:`FunctionTool` instances.
        """
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
