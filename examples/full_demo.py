import logging
from owl.models.registry import ModelRegistry
from owl.skills.registry import SkillRegistry
from owl.skills.web_search import WebSearchSkill
from owl.skills.code_execution import CodeExecutionSkill
from owl.rag.grpc_adapter import GrpcRAGAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing OWL-Workbench full demo...")

    # 1. Models
    try:
        registry = ModelRegistry.from_yaml("config/models_default.yaml")
        # List configured roles
        logger.info(f"Loaded model roles: {list(registry._entries.keys())}")
    except Exception as e:
        logger.error(f"Failed to load registry: {e}")

    # 2. Skills
    skill_registry = SkillRegistry()
    skill_registry.register(WebSearchSkill())
    skill_registry.register(CodeExecutionSkill())
    logger.info(f"Loaded skills: {list(skill_registry.list_registered().keys())}")

    # 3. Agents Setup
    system_prompt = skill_registry.assemble_system_prompt()
    logger.info(f"Assembled System Prompt Length: {len(system_prompt)}")

    tools = skill_registry.aggregate_tools()
    logger.info(f"Aggregated {len(tools)} tools.")

    # 4. RAG
    rag = GrpcRAGAdapter("localhost:50051")
    rag_result = rag.query("How to bake a cake?")
    logger.info(f"RAG result: {rag_result}")

    logger.info("OWL-Workbench full demo completed successfully!")

if __name__ == "__main__":
    main()
