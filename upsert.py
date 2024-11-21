import argparse
from typing import List, Optional
import pandas as pd
import os
from src.client import get_colivara_client
from src.data_loader import load_data
from src.document_manager import upsert_documents

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
    "tatdqa_test.pkl",
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
    "tatdqa_test",
]

# Ensure the output directory exists
os.makedirs("out", exist_ok=True)
client = get_colivara_client()


def process_file(
    file_name: str,
    collection_name: str,
    n_rows: Optional[int],
    run_upsert: bool,
):
    df: pd.DataFrame = load_data(f"data/full/{file_name}", nrows=n_rows)
    os.path.splitext(file_name)[0]

    if run_upsert:
        # Upsert documents and ensure all are added
        results: List[str] = upsert_documents(client, df, collection_name)
        print(f"Total documents upserted for {file_name}: {len(results)}")


def main(
    n_rows: Optional[int],
    run_upsert: bool,
    all_files: bool,
    specific_file: Optional[str],
    collection_name: Optional[str],
) -> None:
    if all_files:
        for file_name, coll_name in zip(DOCUMENT_FILES, COLLECTION_NAMES):
            print(f"\nProcessing {file_name} with collection {coll_name}...")
            process_file(file_name, coll_name, n_rows, run_upsert)
    elif specific_file:
        if specific_file in DOCUMENT_FILES:
            # Use the specified collection name if provided, otherwise use default
            coll_name = (
                collection_name
                if collection_name
                else COLLECTION_NAMES[DOCUMENT_FILES.index(specific_file)]
            )
            print(f"\nProcessing {specific_file} with collection {coll_name}...")
            process_file(specific_file, coll_name, n_rows, run_upsert)
        else:
            print(
                f"Error: {specific_file} is not in the list of available document files."
            )
    else:
        print("Error: Please specify --all_files or --specific_file <filename>.")


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
        args.all_files,
        args.specific_file,
        args.collection_name,
    )
