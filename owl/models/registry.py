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
ModelRegistry — Pluggable model configuration for OWL agents.

Provides a YAML-driven registry that maps agent roles (e.g., "web_agent",
"planning_agent") to specific LLM backends. This eliminates the need for
separate run_*.py files per model provider and enables model swapping
without code changes.

Usage:
    registry = ModelRegistry.from_yaml("config/models_default.yaml")
    web_model = registry.get("web_agent")
    planning_model = registry.get("planning_agent")

Addresses: https://github.com/camel-ai/owl/issues/57
"""

import threading
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from camel.logger import get_logger
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

logger = get_logger(__name__)

# ─── Platform and model type mappings ────────────────────────────────────────
# These map human-readable YAML strings to CAMEL enum values.

PLATFORM_MAP: Dict[str, ModelPlatformType] = {
    "openai": ModelPlatformType.OPENAI,
    "anthropic": ModelPlatformType.ANTHROPIC,
    "deepseek": ModelPlatformType.DEEPSEEK,
    "gemini": ModelPlatformType.GEMINI,
    "groq": ModelPlatformType.GROQ,
    "qwen": ModelPlatformType.QWEN,
    "vllm": ModelPlatformType.VLLM,
    "mistral": ModelPlatformType.MISTRAL,
    "ollama": ModelPlatformType.OLLAMA,
}

# Commonly used model types — extend as needed.
# For types not listed here, the registry falls back to getattr(ModelType, ...).
MODEL_TYPE_MAP: Dict[str, ModelType] = {
    # OpenAI
    "gpt-4o": ModelType.GPT_4O,
    "gpt-4o-mini": ModelType.GPT_4O_MINI,
    "gpt-4-turbo": ModelType.GPT_4_TURBO,
    "o3-mini": ModelType.O3_MINI,
    # DeepSeek
    "deepseek-chat": ModelType.DEEPSEEK_CHAT,
    "deepseek-reasoner": ModelType.DEEPSEEK_REASONER,
}


class ModelRegistryError(Exception):
    """Raised when a model registry operation fails."""


class ModelRegistry:
    """Thread-safe registry that maps agent role names to LLM model instances.

    The registry can be populated programmatically via :meth:`register` or
    declaratively via :meth:`from_yaml`.  Once populated, call :meth:`get` to
    obtain a ready-to-use CAMEL model backend for any registered role.

    Example::

        registry = ModelRegistry()
        registry.register(
            role="web_agent",
            platform="openai",
            model_type="gpt-4o-mini",
            config={"temperature": 0},
        )
        model = registry.get("web_agent")
    """

    _instance: Optional["ModelRegistry"] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._entries: Dict[str, Dict[str, Any]] = {}
        self._cache: Dict[str, Any] = {}

    # ── Singleton access (optional) ──────────────────────────────────────

    @classmethod
    def instance(cls) -> "ModelRegistry":
        """Return a global singleton registry (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the global singleton — primarily for testing."""
        with cls._lock:
            cls._instance = None

    # ── Registration ─────────────────────────────────────────────────────

    def register(
        self,
        role: str,
        platform: str,
        model_type: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a model specification for a given agent role.

        Args:
            role: Agent role name (e.g., ``"web_agent"``, ``"planning_agent"``).
            platform: Model platform key (e.g., ``"openai"``, ``"deepseek"``).
            model_type: Model type key (e.g., ``"gpt-4o-mini"``).
            config: Optional model config dict (e.g., ``{"temperature": 0}``).

        Raises:
            ModelRegistryError: If the platform is not supported.
        """
        platform_lower = platform.lower()
        if platform_lower not in PLATFORM_MAP:
            raise ModelRegistryError(
                f"Unsupported platform '{platform}'. "
                f"Supported: {list(PLATFORM_MAP.keys())}"
            )
        self._entries[role] = {
            "platform": platform_lower,
            "model_type": model_type,
            "config": config or {},
        }
        # Invalidate cache for this role if it was previously resolved.
        self._cache.pop(role, None)
        logger.debug(f"Registered model for role '{role}': {platform}/{model_type}")

    # ── Retrieval ────────────────────────────────────────────────────────

    def get(self, role: str, use_cache: bool = True) -> Any:
        """Retrieve (and lazily create) the model instance for a role.

        Args:
            role: The agent role name.
            use_cache: If ``True``, return a cached instance if available.

        Returns:
            A CAMEL model backend instance created via ``ModelFactory.create``.

        Raises:
            ModelRegistryError: If the role is not registered or model
                creation fails.
        """
        if use_cache and role in self._cache:
            return self._cache[role]

        if role not in self._entries:
            raise ModelRegistryError(
                f"No model registered for role '{role}'. "
                f"Registered roles: {list(self._entries.keys())}"
            )

        entry = self._entries[role]
        platform_enum = PLATFORM_MAP[entry["platform"]]
        model_type_enum = self._resolve_model_type(entry["model_type"])

        try:
            model = ModelFactory.create(
                model_platform=platform_enum,
                model_type=model_type_enum,
                model_config_dict=entry.get("config", {}),
            )
        except Exception as exc:
            raise ModelRegistryError(
                f"Failed to create model for role '{role}': {exc}"
            ) from exc

        if use_cache:
            self._cache[role] = model
        logger.info(
            f"Created model for role '{role}': "
            f"{entry['platform']}/{entry['model_type']}"
        )
        return model

    # ── Bulk loading from YAML ───────────────────────────────────────────

    @classmethod
    def from_yaml(cls, config_path: str) -> "ModelRegistry":
        """Create a new registry pre-populated from a YAML config file.

        The YAML file must have a top-level ``models`` key mapping role names
        to their model specifications::

            models:
              web_agent:
                platform: openai
                model_type: gpt-4o-mini
                config:
                  temperature: 0

        Args:
            config_path: Path to the YAML config file.

        Returns:
            A new :class:`ModelRegistry` instance with all roles registered.

        Raises:
            ModelRegistryError: If the file cannot be read or parsed.
        """
        path = Path(config_path)
        if not path.exists():
            raise ModelRegistryError(f"Config file not found: {config_path}")

        try:
            with open(path, "r", encoding="utf-8") as fh:
                raw = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            raise ModelRegistryError(
                f"Failed to parse YAML config '{config_path}': {exc}"
            ) from exc

        if not isinstance(raw, dict) or "models" not in raw:
            raise ModelRegistryError(
                f"Config file '{config_path}' must have a top-level 'models' key."
            )

        registry = cls()
        for role, spec in raw["models"].items():
            if not isinstance(spec, dict):
                raise ModelRegistryError(
                    f"Model spec for role '{role}' must be a dict, got {type(spec).__name__}."
                )
            platform = spec.get("platform")
            model_type = spec.get("model_type")
            if not platform or not model_type:
                raise ModelRegistryError(
                    f"Model spec for role '{role}' must include 'platform' and 'model_type'."
                )
            registry.register(
                role=role,
                platform=platform,
                model_type=model_type,
                config=spec.get("config"),
            )

        logger.info(
            f"Loaded {len(registry._entries)} model(s) from '{config_path}'"
        )
        return registry

    # ── Introspection ────────────────────────────────────────────────────

    def list_registered(self) -> Dict[str, Dict[str, Any]]:
        """Return a copy of all registered role→model entries."""
        return {role: dict(spec) for role, spec in self._entries.items()}

    def has_role(self, role: str) -> bool:
        """Check if a role is registered."""
        return role in self._entries

    def __contains__(self, role: str) -> bool:
        return self.has_role(role)

    def __repr__(self) -> str:
        roles = list(self._entries.keys())
        return f"ModelRegistry(roles={roles})"

    # ── Internal helpers ─────────────────────────────────────────────────

    @staticmethod
    def _resolve_model_type(model_type_str: str) -> ModelType:
        """Resolve a model type string to a CAMEL ModelType enum.

        Tries the explicit map first, then falls back to ``getattr``.
        """
        if model_type_str in MODEL_TYPE_MAP:
            return MODEL_TYPE_MAP[model_type_str]

        # Fallback: try uppercase with underscores (e.g., "gpt_4o" -> "GPT_4O")
        attr_name = model_type_str.upper().replace("-", "_")
        try:
            return getattr(ModelType, attr_name)
        except AttributeError:
            raise ModelRegistryError(
                f"Unknown model type '{model_type_str}'. "
                f"Known types: {list(MODEL_TYPE_MAP.keys())} "
                f"(or any valid ModelType attribute name)."
            )
