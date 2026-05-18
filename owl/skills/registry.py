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
SkillRegistry — Discover, register, and compose skills onto agents.

The registry maintains a collection of :class:`Skill` instances and can
compose them into a :class:`ChatAgent` by merging their tools and system
prompt fragments.

Example::

    registry = SkillRegistry()
    registry.register(WebSearchSkill(model=web_model))
    registry.register(SummarizerSkill(model=doc_model))

    agent = registry.compose_agent(
        skill_names=["web_search", "summarizer"],
        model=agent_model,
    )
"""

from typing import Dict, List, Optional

from camel.agents import ChatAgent
from camel.logger import get_logger

from .base import Skill

logger = get_logger(__name__)


class SkillRegistryError(Exception):
    """Raised when a skill registry operation fails."""


class SkillRegistry:
    """Registry for discovering and composing agent skills.

    Skills are registered by their unique ``name`` property.  The registry
    can then compose a :class:`ChatAgent` from a list of skill names,
    automatically merging their tools and system prompts.
    """

    def __init__(self) -> None:
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """Register a skill instance.

        Args:
            skill: The skill to register.

        Raises:
            SkillRegistryError: If a skill with the same name is already
                registered.
        """
        if not isinstance(skill, Skill):
            raise SkillRegistryError(
                f"Expected a Skill instance, got {type(skill).__name__}."
            )
        if skill.name in self._skills:
            logger.warning(
                f"Overwriting existing skill '{skill.name}' in registry."
            )
        self._skills[skill.name] = skill
        logger.debug(f"Registered skill: {skill.name}")

    def get(self, name: str) -> Skill:
        """Retrieve a registered skill by name.

        Args:
            name: The skill name.

        Returns:
            The registered :class:`Skill` instance.

        Raises:
            SkillRegistryError: If the skill is not found.
        """
        if name not in self._skills:
            raise SkillRegistryError(
                f"Skill '{name}' not found. "
                f"Available: {list(self._skills.keys())}"
            )
        return self._skills[name]

    def list_registered(self) -> Dict[str, Dict[str, str]]:
        """Return a mapping of skill name → metadata."""
        return {name: {"description": skill.description} for name, skill in self._skills.items()}

    def list_skills(self) -> Dict[str, str]:
        """Return a mapping of skill name → description."""
        return {name: skill.description for name, skill in self._skills.items()}

    def has_skill(self, name: str) -> bool:
        """Check if a skill is registered."""
        return name in self._skills

    def compose_agent(
        self,
        skill_names: List[str],
        model,
        base_system_prompt: Optional[str] = None,
        **agent_kwargs,
    ) -> ChatAgent:
        """Compose a ChatAgent from multiple skills.

        Merges the tools and system prompt fragments from the specified
        skills into a single agent.

        Args:
            skill_names: List of skill names to compose.
            model: The CAMEL model backend for the agent.
            base_system_prompt: Optional base system prompt.  Skill prompt
                fragments are appended after this.
            **agent_kwargs: Additional keyword arguments for ``ChatAgent``.

        Returns:
            A configured :class:`ChatAgent` instance.

        Raises:
            SkillRegistryError: If any skill name is not registered.
        """
        tools = []
        prompt_parts = []

        if base_system_prompt:
            prompt_parts.append(base_system_prompt)

        for name in skill_names:
            skill = self.get(name)
            tools.extend(skill.get_tools())
            fragment = skill.system_prompt_fragment.strip()
            if fragment:
                prompt_parts.append(fragment)

        system_prompt = "\n\n".join(prompt_parts) if prompt_parts else ""

        agent = ChatAgent(
            system_prompt,
            model=model,
            tools=tools,
            **agent_kwargs,
        )

        logger.info(
            f"Composed agent with skills: {skill_names} "
            f"({len(tools)} tools, {len(prompt_parts)} prompt fragments)"
        )
        return agent

    def __contains__(self, name: str) -> bool:
        return self.has_skill(name)

    def assemble_system_prompt(self) -> str:
        """Assemble a concatenated system prompt from all registered skills."""
        parts = [s.system_prompt_fragment.strip() for s in self._skills.values() if s.system_prompt_fragment.strip()]
        return "\n".join(parts)

    def aggregate_tools(self) -> list:
        """Aggregate tools from all registered skills."""
        tools = []
        for skill in self._skills.values():
            tools.extend(skill.get_tools())
        return tools

    def __repr__(self) -> str:
        return f"SkillRegistry(skills={list(self._skills.keys())})"
