import argparse
from typing import List, Optional
import pandas as pd
import os
from src.client import get_colivara_client
from src.data_loader import load_data
from src.document_manager import upsert_documents
from src.evaluator import evaluate_rag_model

# List of document files
DOCUMENT_FILES = [
    "arxivqa_test_subsampled.pkl",
    "docvqa_test_subsampled.pkl",
    "infovqa_test_subsampled.pkl",
    "shiftproject_test.pkl",
    "syntheticDocQA_artificial_intelligence_test.pkl",
    "syntheticDocQA_energy_test.pkl",
    "syntheticDocQA_government_reports_test.pkl",
    "syntheticDocQA_healthcare_industry_test.pkl",
    "tabfquad_test_subsampled.pkl",
    "tatqa_test_subsampled.pkl",
]

# Corresponding list of collection names
COLLECTION_NAMES = [
    "arxivqa_collection",
    "docvqa_collection",
    "infovqa_collection",
    "shiftproject_collection",
    "synthetic_ai_collection",
    "synthetic_energy_collection",
    "synthetic_gov_reports_collection",
    "synthetic_healthcare_collection",
    "tabfquad_collection",
    "tatqa_collection",
]

# Ensure the output directory exists
os.makedirs("out", exist_ok=True)

# Lists to store scores for DataFrames
avg_ndcg_scores_list = []
ndcg_scores_dict = {}


def process_file(
    file_name: str,
    collection_name: str,
    n_rows: Optional[int],
    run_upsert: bool,
    run_evaluate: bool,
):
    client = get_colivara_client()
    df: pd.DataFrame = load_data(f"data/{file_name}", nrows=n_rows)
    base_file_name = os.path.splitext(file_name)[0]

    if run_upsert:
        # Upsert documents and ensure all are added
        results: List[str] = upsert_documents(client, df, collection_name)
        print(f"Total documents upserted for {file_name}: {len(results)}")

    if run_evaluate:
        # Evaluate the RAG model
        avg_ndcg_score: float
        ndcg_scores: List[float]
        avg_ndcg_score, ndcg_scores = evaluate_rag_model(df, client, collection_name)

        # Store results for avg_ndcg_score DataFrame
        avg_ndcg_scores_list.append(
            {"filename": base_file_name, "avg_ndcg_score": avg_ndcg_score}
        )
        # Store results for ndcg_scores DataFrame
        ndcg_scores_dict[base_file_name] = ndcg_scores

        print(f"Average NDCG@5 Score for {file_name}: {avg_ndcg_score:.4f}")


def main(
    n_rows: Optional[int],
    run_upsert: bool,
    run_evaluate: bool,
    all_files: bool,
    specific_file: Optional[str],
    collection_name: Optional[str],
) -> None:
    if all_files:
        for file_name, coll_name in zip(DOCUMENT_FILES, COLLECTION_NAMES):
            print(f"\nProcessing {file_name} with collection {coll_name}...")
            process_file(file_name, coll_name, n_rows, run_upsert, run_evaluate)
    elif specific_file:
        if specific_file in DOCUMENT_FILES:
            # Use the specified collection name if provided, otherwise use default
            coll_name = (
                collection_name
                if collection_name
                else COLLECTION_NAMES[DOCUMENT_FILES.index(specific_file)]
            )
            print(f"\nProcessing {specific_file} with collection {coll_name}...")
            process_file(specific_file, coll_name, n_rows, run_upsert, run_evaluate)
        else:
            print(
                f"Error: {specific_file} is not in the list of available document files."
            )
    else:
        print("Error: Please specify --all_files or --specific_file <filename>.")

    # After processing all files, create DataFrames and save as CSV
    if run_evaluate:
        # DataFrame for avg_ndcg_score
        avg_ndcg_df = pd.DataFrame(avg_ndcg_scores_list)
        avg_ndcg_df.to_pickle("out/avg_ndcg_scores.pkl")

        # DataFrame for ndcg_scores with NaN padding for different lengths
        ndcg_scores_df = pd.DataFrame(
            dict([(k, pd.Series(v)) for k, v in ndcg_scores_dict.items()])
        )
        ndcg_scores_df.to_pickle("out/ndcg_scores.pkl")

        print("Average NDCG scores saved to out/avg_ndcg_scores.pkl")
        print("Detailed NDCG scores saved to out/ndcg_scores.pkl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run RAG model evaluation or upsert documents."
    )
    parser.add_argument(
        "--n_rows",
        type=int,
        default=None,
        help="Number of rows to load from data (optional, loads all if not specified)",
    )
    parser.add_argument(
        "--upsert", action="store_true", help="Flag to upsert documents"
    )
    parser.add_argument(
        "--evaluate", action="store_true", help="Flag to evaluate the RAG model"
    )
    parser.add_argument(
        "--all_files", action="store_true", help="Flag to process all document files"
    )
    parser.add_argument(
        "--specific_file",
        type=str,
        help="Specify a single file to process (should be one of the listed document files)",
    )
    parser.add_argument(
        "--collection_name",
        type=str,
        help="Specify a collection name for a specific file (optional, defaults to predefined collection if not specified)",
    )

    args = parser.parse_args()
    main(
        args.n_rows,
        args.upsert,
        args.evaluate,
        args.all_files,
        args.specific_file,
        args.collection_name,
    )
