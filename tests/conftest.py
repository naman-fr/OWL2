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
Shared test fixtures for the OWL test suite.

All fixtures use mocks to avoid requiring API keys or network access.
"""

from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
import yaml

# ── Paths ────────────────────────────────────────────────────────────────

@pytest.fixture
def project_root() -> Path:
    """Return the OWL project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def config_dir(project_root) -> Path:
    """Return the config directory."""
    return project_root / "config"


# ── YAML config fixtures ────────────────────────────────────────────────

@pytest.fixture
def sample_config_dict() -> Dict[str, Any]:
    """Return a valid model config dict for testing."""
    return {
        "models": {
            "web_agent": {
                "platform": "openai",
                "model_type": "gpt-4o-mini",
                "config": {"temperature": 0},
            },
            "planning_agent": {
                "platform": "deepseek",
                "model_type": "deepseek-chat",
                "config": {"temperature": 0.1},
            },
            "reasoning_agent": {
                "platform": "openai",
                "model_type": "gpt-4o",
                "config": {"temperature": 0, "max_tokens": 4096},
            },
        }
    }


@pytest.fixture
def sample_config_file(sample_config_dict, tmp_path) -> Path:
    """Write sample config to a temp YAML file and return its path."""
    config_path = tmp_path / "test_models.yaml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config_dict, f)
    return config_path


@pytest.fixture
def invalid_config_file(tmp_path) -> Path:
    """Write an invalid YAML config (missing required fields)."""
    config_path = tmp_path / "invalid_models.yaml"
    with open(config_path, "w") as f:
        yaml.dump({"models": {"bad_agent": {"platform": "openai"}}}, f)
    return config_path


@pytest.fixture
def empty_config_file(tmp_path) -> Path:
    """Write a config file without the 'models' key."""
    config_path = tmp_path / "empty_models.yaml"
    with open(config_path, "w") as f:
        yaml.dump({"other_key": "value"}, f)
    return config_path


# ── Mock model fixtures ─────────────────────────────────────────────────

@pytest.fixture
def mock_model():
    """Return a mock CAMEL model backend."""
    model = MagicMock()
    model.model_type = "mock-model"
    model.model_platform = "mock-platform"
    return model


@pytest.fixture
def mock_model_factory():
    """Patch ModelFactory.create to return a mock model."""
    with patch("owl.models.registry.ModelFactory") as mock_factory:
        mock_instance = MagicMock()
        mock_factory.create.return_value = mock_instance
        yield mock_factory


# ── Mock agent fixtures ─────────────────────────────────────────────────

@pytest.fixture
def mock_chat_agent():
    """Return a mock ChatAgent."""
    agent = MagicMock()
    agent.system_message = MagicMock()
    agent.system_message.content = "Test system message"
    return agent


# ── Skill fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def mock_skill():
    """Return a mock Skill instance with all required properties."""
    from owl.skills.base import Skill

    class MockSkill(Skill):
        @property
        def name(self) -> str:
            return "mock_skill"

        @property
        def description(self) -> str:
            return "A mock skill for testing."

        @property
        def system_prompt_fragment(self) -> str:
            return "You have mock capabilities."

        def get_tools(self) -> list:
            return [MagicMock()]

    return MockSkill()


@pytest.fixture
def mock_skill_alt():
    """Return a second mock Skill with a different name."""
    from owl.skills.base import Skill

    class AltMockSkill(Skill):
        @property
        def name(self) -> str:
            return "alt_skill"

        @property
        def description(self) -> str:
            return "An alternative mock skill."

        @property
        def system_prompt_fragment(self) -> str:
            return "You have alternative capabilities."

        def get_tools(self) -> list:
            return [MagicMock(), MagicMock()]

    return AltMockSkill()
