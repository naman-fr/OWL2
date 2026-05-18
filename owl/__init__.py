# -*- coding: utf-8 -*-
"""Top-level package for OWL.

This file makes the ``owl`` directory a proper Python package so that imports
such as ``import owl.models.registry`` work correctly when running the test
suite from the repository root.

It also re‑exports the most commonly used public modules for convenience.
"""

from . import (
    models,  # noqa: F401
    skills,  # noqa: F401
)

__all__ = ["models", "skills"]
