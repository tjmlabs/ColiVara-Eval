import argparse
from typing import Optional
import pandas as pd
from datetime import datetime
import os
from src.evaluator import evaluate_rag_model
from tenacity import retry, stop_after_attempt, wait_fixed


def initialize_client(api_key: str):
    from colivara_py import Colivara

    return Colivara(base_url="https://api.colivara.com", api_key=api_key)


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# List of query files
QUERY_FILES = [
    "arxivqa_test_subsampled_queries.pkl",
    "docvqa_test_subsampled_queries.pkl",
    "infovqa_test_subsampled_queries.pkl",
    "shiftproject_test_queries.pkl",
    "syntheticDocQA_artificial_intelligence_test_queries.pkl",
    "syntheticDocQA_energy_test_queries.pkl",
    "syntheticDocQA_government_reports_test_queries.pkl",
    "syntheticDocQA_healthcare_industry_test_queries.pkl",
    "tabfquad_test_subsampled_queries.pkl",
    "tatqa_test_subsampled_queries.pkl",
]

# Corresponding list of collection names
COLLECTION_NAMES = [
    "arxivqa_test_subsampled",
    "docvqa_test_subsampled",
    "infovqa_test_subsampled",
    "shiftproject_test",
    "syntheticDocQA_artificial_intelligence_test",
    "syntheticDocQA_energy_test",
    "syntheticDocQA_government_reports_test",
    "syntheticDocQA_healthcare_industry_test",
    "tabfquad_test_subsampled",
    "tatqa_test_subsampled",
]

# Ensure the output directory exists
os.makedirs("out", exist_ok=True)

# Lists to store scores for DataFrames
avg_ndcg_scores_list = []
ndcg_scores_dict = {}


def validate_api_key(api_key: str) -> bool:
    """
    Validate the provided API key by attempting to initialize the client.

    Args:
        api_key (str): The API key to validate.

    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    try:
        client = initialize_client(api_key=api_key)
        # Attempt to get some basic info to validate the key
        client.list_collections()
        return True
    except Exception:
        return False


@retry(
    stop=stop_after_attempt(5),  # Retry up to 5 times
    wait=wait_fixed(2),  # Wait 2 seconds between attempts
)
def evaluate_with_retry(queries_df, client, collection_name):
    """Wrapper around evaluate_rag_model to add retry mechanism."""
    return evaluate_rag_model(queries_df, client, collection_name)


def process_file(
    query_file: str,
    collection_name: str,
    n_rows: Optional[int],
    api_key: str,
):
    client = initialize_client(api_key=api_key)
    queries_df: pd.DataFrame = pd.read_pickle(f"data/queries/{query_file}")
    queries_df.dropna(subset=["query"], inplace=True)
    if n_rows is not None:
        queries_df = queries_df.head(n_rows).copy()  # Create a copy to avoid warnings
    base_file_name = os.path.splitext(query_file)[0]

    # Evaluate the RAG model with retry logic
    avg_ndcg_score, ndcg_scores, avg_latency = evaluate_with_retry(
        queries_df, client, collection_name
    )
    collection_info = client.get_collection(collection_name)
    num_documents = collection_info.num_documents  # Retrieve document count

    # Store results for avg_ndcg_score DataFrame
    avg_ndcg_scores_list.append(
        {
            "filename": base_file_name,
            "avg_ndcg_score": avg_ndcg_score,
            "avg_latency": avg_latency,
            "num_docs": num_documents,
        }
    )
    # Store results for ndcg_scores DataFrame
    ndcg_scores_dict[base_file_name] = ndcg_scores

    print(f"Average NDCG@5 Score for {query_file}: {avg_ndcg_score:.4f}")


def main(
    n_rows: Optional[int],
    all_files: bool,
    collection_name: Optional[str],
    api_key: str,
) -> None:
    if not validate_api_key(api_key):
        print("Error: Invalid API key provided.")
        return

    if all_files:
        for query_file, coll_name in zip(QUERY_FILES, COLLECTION_NAMES):
            print(f"\nProcessing {query_file} with collection {coll_name}...")
            process_file(query_file, coll_name, n_rows, api_key)
    elif collection_name:
        if collection_name in COLLECTION_NAMES:
            query_file = QUERY_FILES[COLLECTION_NAMES.index(collection_name)]
            print(f"\nProcessing {query_file} with collection {collection_name}...")
            process_file(query_file, collection_name, n_rows, api_key)
        else:
            print(
                f"Error: {collection_name} is not in the list of available collections."
            )
            return
    else:
        print("Error: Please specify --all_files or --collection_name <name>.")

    # After processing all files, create DataFrames and save as CSV
    # DataFrame for avg_ndcg_score
    avg_ndcg_df = pd.DataFrame(avg_ndcg_scores_list)
    if all_files:
        avg_ndcg_df.to_pickle(f"out/avg_ndcg_scores_{timestamp}.pkl")
    else:
        avg_ndcg_df.to_pickle(f"out/avg_ndcg_scores_{collection_name}_{timestamp}.pkl")

    # DataFrame for ndcg_scores with NaN padding for different lengths
    ndcg_scores_df = pd.DataFrame(
        dict([(k, pd.Series(v)) for k, v in ndcg_scores_dict.items()])
    )
    if all_files:
        ndcg_scores_df.to_pickle(f"out/ndcg_scores_{timestamp}.pkl")
    else:
        ndcg_scores_df.to_pickle(f"out/ndcg_scores_{collection_name}_{timestamp}.pkl")

    print("Average NDCG scores saved to out/avg_ndcg_scores.pkl")
    print("Detailed NDCG scores saved to out/ndcg_scores.pkl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate the RAG model using query data."
    )
    parser.add_argument(
        "--n_rows",
        type=int,
        default=None,
        help="Number of rows to load from query data (optional, loads all if not specified)",
    )
    parser.add_argument(
        "--all_files", action="store_true", help="Flag to process all query files"
    )
    parser.add_argument(
        "--collection_name",
        type=str,
        help="Specify a collection name to process (should be one of the listed collections)",
    )
    parser.add_argument(
        "--api_key",
        type=str,
        required=True,
        help="API key for accessing the Colivara client",
    )

    args = parser.parse_args()
    main(
        args.n_rows,
        args.all_files,
        args.collection_name,
        args.api_key,
    )
