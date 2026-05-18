import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate the OWL planner model.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the trained model.")
    parser.add_argument("--test_data", type=str, default="data/planner_examples/test.jsonl", help="Path to test dataset.")
    return parser.parse_args()

def main():
    args = parse_args()
    logger.info(f"Evaluating model at {args.model_path} on {args.test_data}")
    
    # Mock evaluation metrics
    logger.info("Running evaluation metrics...")
    results = {
        "exact_match": 0.85,
        "rougeL": 0.76,
        "token_cost_avg": 120.5
    }
    
    logger.info("Evaluation results:")
    for metric, val in results.items():
        logger.info(f"  {metric}: {val}")

if __name__ == "__main__":
    main()
