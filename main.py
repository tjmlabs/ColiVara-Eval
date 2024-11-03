import argparse
from typing import List
import pandas as pd
from src.client import get_colivara_client
from src.data_loader import load_data
from src.document_manager import upsert_documents
from src.evaluator import evaluate_rag_model


def main(collection_name: str, n_rows: int) -> None:
    """
    Main function to run the RAG model evaluation.

    Args:
        collection_name (str): The name of the collection.
        n_rows (int): The number of rows to load from the data.
    """
    # Ensure n_rows does not exceed 500
    if n_rows > 500:
        print("n_rows exceeds the maximum limit of 500. Setting n_rows to 500.")
        n_rows = 500

    client = get_colivara_client()
    df: pd.DataFrame = load_data("data/docvqa_test_subsampled.pkl", nrows=n_rows)

    # Upsert documents and ensure all are added
    results: List[str] = upsert_documents(client, df, collection_name)
    print(f"Total documents upserted: {len(results)}")

    # Evaluate the RAG model
    avg_ndcg_score: float = evaluate_rag_model(df, client, collection_name)
    print(f"Average NDCG@5 Score: {avg_ndcg_score:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run RAG model evaluation with specified parameters."
    )
    parser.add_argument(
        "--collection_name", type=str, required=True, help="Name of the collection"
    )
    parser.add_argument(
        "--n_rows", type=int, required=True, help="Number of rows to load from data"
    )

    args = parser.parse_args()
    main(args.collection_name, args.n_rows)
