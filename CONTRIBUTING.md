# Contributing to OWL-Workbench

First off, thank you for considering contributing to OWL-Workbench! It's people like you that make it such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](https://github.com/camel-ai/owl/issues) first. If it's not there, feel free to open a new one.

## Setting up your environment

1. Clone the repo and navigate into it.
2. We recommend using `uv` or `venv` to create an isolated Python environment:
   ```bash
   uv venv .venv --python=3.11
   source .venv/bin/activate
   pip install -e .
   pip install -r requirements.txt
   pip install ruff pytest pytest-cov
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```
2. Make your changes.
3. Lint your code:
   ```bash
   ruff check .
   ```
4. Run the test suite:
   ```bash
   pytest tests/
   ```
5. Commit your changes with a descriptive message and push your branch.
6. Open a Pull Request and fill out the PR template.

## Adding New Skills

If you want to contribute a new agent skill, please follow the `Skill` interface in `owl/skills/base.py`.
- Ensure your skill exposes tools using `camel.toolkits.FunctionTool`.
- Provide a clear `system_prompt_fragment`.
- Register the skill in `owl/skills/registry.py` or export it in `owl/skills/__init__.py`.

Thank you for your contributions!
