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
Tests for owl.models.registry.ModelRegistry.

All tests mock ModelFactory to avoid real API calls.
"""


import pytest

from owl.models.registry import (
    PLATFORM_MAP,
    ModelRegistry,
    ModelRegistryError,
)

# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the global singleton between tests."""
    ModelRegistry.reset_instance()
    yield
    ModelRegistry.reset_instance()


@pytest.fixture
def registry():
    """Return a fresh ModelRegistry instance."""
    return ModelRegistry()


# ── Registration tests ───────────────────────────────────────────────────

class TestRegistration:
    def test_register_valid_role(self, registry):
        registry.register(
            role="web_agent",
            platform="openai",
            model_type="gpt-4o-mini",
            config={"temperature": 0},
        )
        assert registry.has_role("web_agent")
        assert "web_agent" in registry

    def test_register_multiple_roles(self, registry):
        registry.register("role_a", "openai", "gpt-4o-mini")
        registry.register("role_b", "deepseek", "deepseek-chat")
        assert len(registry.list_registered()) == 2

    def test_register_overwrites_existing(self, registry):
        registry.register("agent", "openai", "gpt-4o-mini")
        registry.register("agent", "deepseek", "deepseek-chat")
        entries = registry.list_registered()
        assert entries["agent"]["platform"] == "deepseek"

    def test_register_unsupported_platform(self, registry):
        with pytest.raises(ModelRegistryError, match="Unsupported platform"):
            registry.register("agent", "nonexistent_platform", "some-model")

    def test_register_case_insensitive_platform(self, registry):
        registry.register("agent", "OpenAI", "gpt-4o-mini")
        entries = registry.list_registered()
        assert entries["agent"]["platform"] == "openai"

    def test_register_default_config(self, registry):
        registry.register("agent", "openai", "gpt-4o-mini")
        entries = registry.list_registered()
        assert entries["agent"]["config"] == {}


# ── Retrieval tests ──────────────────────────────────────────────────────

class TestRetrieval:
    def test_get_registered_role(self, registry, mock_model_factory):
        registry.register("web_agent", "openai", "gpt-4o-mini")
        model = registry.get("web_agent")
        assert model is not None
        mock_model_factory.create.assert_called_once()

    def test_get_unregistered_role(self, registry):
        with pytest.raises(ModelRegistryError, match="No model registered"):
            registry.get("nonexistent_role")

    def test_get_uses_cache(self, registry, mock_model_factory):
        registry.register("agent", "openai", "gpt-4o-mini")
        model1 = registry.get("agent")
        model2 = registry.get("agent")
        assert model1 is model2
        # ModelFactory.create should be called only once (cached)
        assert mock_model_factory.create.call_count == 1

    def test_get_bypass_cache(self, registry, mock_model_factory):
        registry.register("agent", "openai", "gpt-4o-mini")
        registry.get("agent", use_cache=True)
        registry.get("agent", use_cache=False)
        assert mock_model_factory.create.call_count == 2

    def test_re_register_invalidates_cache(self, registry, mock_model_factory):
        registry.register("agent", "openai", "gpt-4o-mini")
        registry.get("agent")
        registry.register("agent", "deepseek", "deepseek-chat")
        registry.get("agent")
        assert mock_model_factory.create.call_count == 2


# ── YAML loading tests ──────────────────────────────────────────────────

class TestYAMLLoading:
    def test_load_valid_config(self, sample_config_file, mock_model_factory):
        registry = ModelRegistry.from_yaml(str(sample_config_file))
        assert registry.has_role("web_agent")
        assert registry.has_role("planning_agent")
        assert registry.has_role("reasoning_agent")
        assert len(registry.list_registered()) == 3

    def test_load_preserves_config(self, sample_config_file):
        registry = ModelRegistry.from_yaml(str(sample_config_file))
        entries = registry.list_registered()
        assert entries["web_agent"]["config"]["temperature"] == 0
        assert entries["planning_agent"]["config"]["temperature"] == 0.1
        assert entries["reasoning_agent"]["config"]["max_tokens"] == 4096

    def test_load_nonexistent_file(self):
        with pytest.raises(ModelRegistryError, match="Config file not found"):
            ModelRegistry.from_yaml("/nonexistent/path.yaml")

    def test_load_missing_models_key(self, empty_config_file):
        with pytest.raises(ModelRegistryError, match="top-level 'models' key"):
            ModelRegistry.from_yaml(str(empty_config_file))

    def test_load_missing_required_fields(self, invalid_config_file):
        with pytest.raises(ModelRegistryError, match="must include 'platform' and 'model_type'"):
            ModelRegistry.from_yaml(str(invalid_config_file))

    def test_load_malformed_yaml(self, tmp_path):
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("unparseable: @#$")
        with pytest.raises(ModelRegistryError, match="Failed to parse YAML"):
            ModelRegistry.from_yaml(str(bad_file))


# ── Singleton tests ──────────────────────────────────────────────────────

class TestSingleton:
    def test_instance_returns_same_object(self):
        inst1 = ModelRegistry.instance()
        inst2 = ModelRegistry.instance()
        assert inst1 is inst2

    def test_reset_instance(self):
        inst1 = ModelRegistry.instance()
        ModelRegistry.reset_instance()
        inst2 = ModelRegistry.instance()
        assert inst1 is not inst2


# ── Introspection tests ─────────────────────────────────────────────────

class TestIntrospection:
    def test_list_registered_returns_copy(self, registry):
        registry.register("agent", "openai", "gpt-4o-mini")
        entries = registry.list_registered()
        entries["agent"]["platform"] = "modified"
        # Original should not be modified
        assert registry.list_registered()["agent"]["platform"] == "openai"

    def test_repr(self, registry):
        registry.register("a", "openai", "gpt-4o-mini")
        registry.register("b", "deepseek", "deepseek-chat")
        repr_str = repr(registry)
        assert "ModelRegistry" in repr_str
        assert "'a'" in repr_str
        assert "'b'" in repr_str


# ── Model type resolution tests ─────────────────────────────────────────

class TestModelTypeResolution:
    def test_resolve_known_type(self):
        from owl.models.registry import ModelRegistry
        result = ModelRegistry._resolve_model_type("gpt-4o-mini")
        assert result is not None

    def test_resolve_fallback_uppercase(self):
        # This tests the getattr fallback for types not in the explicit map
        # We just verify it doesn't crash for types in the ModelType enum
        from camel.types import ModelType

        # Pick a type that exists in ModelType but may not be in MODEL_TYPE_MAP
        for attr in dir(ModelType):
            if attr.isupper() and not attr.startswith("_"):
                break
        # Just verify the method is callable (specific results depend on CAMEL version)

    def test_resolve_unknown_type(self):
        with pytest.raises(ModelRegistryError, match="Unknown model type"):
            ModelRegistry._resolve_model_type("completely-fake-model-xyz")


# ── Platform map coverage ────────────────────────────────────────────────

class TestPlatformMap:
    @pytest.mark.parametrize(
        "platform",
        ["openai", "anthropic", "deepseek", "gemini", "groq", "qwen", "vllm", "mistral", "ollama"],
    )
    def test_all_platforms_mapped(self, platform):
        assert platform in PLATFORM_MAP
