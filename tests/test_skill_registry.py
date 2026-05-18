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
Tests for owl.skills.registry.SkillRegistry and the example skills.
"""

from owl.skills.registry import SkillRegistry


def test_skill_registry_register_and_get(mock_skill, mock_skill_alt):
    registry = SkillRegistry()
    # Register two distinct skills
    registry.register(mock_skill)
    registry.register(mock_skill_alt)
    # Retrieval
    assert registry.get("mock_skill") is mock_skill
    assert registry.get("alt_skill") is mock_skill_alt
    # Duplicate registration overwrites
    registry.register(mock_skill_alt)  # same name as alt_skill, should replace
    assert registry.get("alt_skill") is mock_skill_alt


def test_skill_registry_introspection(mock_skill):
    registry = SkillRegistry()
    registry.register(mock_skill)
    names = registry.list_registered()
    assert "mock_skill" in names
    assert isinstance(names["mock_skill"], dict)
    assert names["mock_skill"]["description"] == mock_skill.description


def test_skill_registry_system_prompt_assembly(mock_skill, mock_skill_alt):
    registry = SkillRegistry()
    registry.register(mock_skill)
    registry.register(mock_skill_alt)
    # The assembled prompt should concatenate the fragments in registration order
    assembled = registry.assemble_system_prompt()
    expected = f"{mock_skill.system_prompt_fragment}\n{mock_skill_alt.system_prompt_fragment}"
    assert assembled.strip() == expected.strip()


def test_skill_registry_tool_aggregation(mock_skill, mock_skill_alt):
    registry = SkillRegistry()
    registry.register(mock_skill)
    registry.register(mock_skill_alt)
    tools = registry.aggregate_tools()
    # Should contain tools from both skill mocks (2+1 = 3)
    assert len(tools) == 3
    # Ensure each tool is a MagicMock (as defined in fixtures)
    for tool in tools:
        assert hasattr(tool, "__call__")


import pytest


def test_skill_registry_error_on_missing(mock_skill):
    registry = SkillRegistry()
    registry.register(mock_skill)
    with pytest.raises(Exception, match="Skill 'nonexistent' not found"):
        registry.get("nonexistent")
