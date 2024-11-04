# Colivara Evaluation Project

This repository contains a comprehensive evaluation of the [Colivara](https://github.com/tjmlabs/ColiVara) API for document management, search, and retrieval, using a Retrieval-Augmented Generation (RAG) model. This evaluation aims to assess Colivara's capabilities in managing document collections, performing efficient search operations, and calculating relevance metrics to measure performance.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Evaluation](#evaluation) 
  - [Collection Management](#collection-management)
- [File Structure](#file-structure)
- [Configuration](#configuration)
- [Technical Details](#technical-details)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Project Overview

The goal of this project is to evaluate Colivara’s document retrieval and management features, particularly for applications that rely on high-performance data search and retrieval. This includes testing Colivara's collection and document management, assessing its suitability for various search and retrieval scenarios, and benchmarking the platform with a RAG model to evaluate relevance based on real-world queries.

## Features

- **Data Loading**: Load document datasets in a structured format for evaluation, with support for processing metadata and converting images to base64.
- **Document Management**: Manage collections and documents, including creation, updating, and deletion.
- **RAG Model Evaluation**: Use NDCG (Normalized Discounted Cumulative Gain) to evaluate the relevance of search results.
- **Collection Management Tool**: A utility for listing, creating, and deleting collections in Colivara.
- **Comprehensive Configurations**: Load configurations from environment variables for easy setup and deployment.

## Requirements

- Python 3.8+
- Colivara API (configured and accessible)
- [colivara-py](https://github.com/tjmlabs/colivara-py) Python client

### Dependencies
The required Python packages are listed in `requirements.txt`, including:
- `pandas`
- `numpy`
- `tqdm`
- `dotenv`
- `colivara_py` (Colivara client library)
- `pytest` (for testing)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/colivara-evaluation.git
   cd colivara-evaluation
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   - Create a `.env` file in the root directory.
   - Add the following variables:
     ```bash
     COLIVARA_API_KEY=your_api_key_here
     COLIVARA_BASE_URL=https://api.colivara.com
     ```
## Usage

The Colivara Evaluation Project provides a streamlined interface for managing and evaluating document collections within Colivara. The primary entry points for usage are `main.py`, for performing document upsert and evaluation, and `collection_manager.py`, which allows for managing collections directly.

### Document Upsert and Evaluation with `main.py`

The `main.py` script enables you to upsert documents into Colivara collections, perform relevance evaluation, or both. It allows selective processing of single datasets or batch processing across all available datasets, making it adaptable for various scenarios.

#### Key Arguments

- **`--n_rows`**: Specify the number of rows to load from the dataset for processing. This is optional; if not provided, the script will load all rows.
- **`--upsert`**: Include this flag if you want to upsert documents into Colivara. 
- **`--evaluate`**: Use this flag to evaluate the RAG model on the specified collection(s) and output the relevance metrics.
- **`--all_files`**: Processes all datasets in the `DOCUMENT_FILES` list.
- **`--specific_file`**: Specify a single file to process by name (must match one of the files in `DOCUMENT_FILES`).
- **`--collection_name`**: Use this to define a custom collection name when processing a specific file. If not provided, the script defaults to the predefined collection name for that file.

### Example Commands

#### 1. Upserting and Evaluating a Single Dataset

To upsert documents from a specific dataset and evaluate relevance, run:
```bash
python main.py --specific_file arxivqa_test_subsampled.pkl --collection_name arxivqa_collection --upsert --evaluate
```

This command will:
- Upsert all documents from `arxivqa_test_subsampled.pkl` into `arxivqa_collection` if it doesn’t already exist.
- Run the evaluation, outputting relevance metrics based on NDCG@5.



#### 2. Evaluating All Datasets without Upserting (Primary Use Case)

To evaluate the relevance of all datasets without performing any upsert operations, use the following command:

```bash
python main.py --all_files --evaluate
```

This command will:
- Perform a relevance evaluation (NDCG@5) on all datasets listed in `DOCUMENT_FILES` without modifying the collections.
- Save the results in the `out/` directory:
  - **`out/avg_ndcg_scores.pkl`** – Contains the average NDCG@5 score for each dataset.
  - **`out/ndcg_scores.pkl`** – Provides detailed NDCG scores for each query.

This example is ideal for scenarios where collections have already been upserted and only relevance metrics are required for ongoing analysis or benchmarking.

#### 3. Processing All Datasets (Upsert and Evaluate)

To upsert documents and evaluate relevance for all datasets:
```bash
python main.py --all_files --upsert --evaluate
```

This command will:
- Loop through all datasets in `DOCUMENT_FILES`, upserting documents into their corresponding collections.
- Evaluate each collection and output the average and detailed NDCG scores to the `out/` directory.

### Collection Management with `collection_manager.py`

The `collection_manager.py` script provides utilities for listing and deleting collections within Colivara.

#### Commands

- **List All Collections**
  ```bash
  python collection_manager.py --list
  ```
  Displays all existing collections within Colivara.

- **Delete a Collection**
  ```bash
  python collection_manager.py --delete <collection_name>
  ```
  Deletes the specified collection. This action is irreversible, so ensure that the correct collection name is provided.

## File Structure

- `src/`
  - `client.py`: Initializes the Colivara client.
  - `config.py`: Loads API key and base URL from environment variables.
  - `data_loader.py`: Handles data loading and base64 image encoding.
  - `document_manager.py`: Manages document upserting and collection creation.
  - `evaluator.py`: Evaluates model performance using NDCG.
- `collection_manager.py`: Provides collection listing and deletion tools.
- `main.py`: Main script for document upsertion and evaluation.
- `tests/`: Contains unit tests for the project.
- `data/`: Stores the dataset for evaluation.
- `.env`: Environment configuration file (not included in version control).
- `requirements.txt`: Lists Python package dependencies.

## Configuration

The project configuration relies on environment variables defined in a `.env` file:
- `COLIVARA_API_KEY`: API key for authenticating with the Colivara service.
- `COLIVARA_BASE_URL`: The base URL for accessing Colivara's API.

Use `dotenv` to load these configurations automatically, ensuring that sensitive information is securely managed.

## Technical Details

### Discounted Cumulative Gain (DCG)

DCG is a measure of relevance that considers the position of relevant results in the returned list. It assigns higher scores to results that appear earlier.

### Normalized Discounted Cumulative Gain (NDCG)

NDCG normalizes DCG by dividing it by the ideal DCG (IDCG) for a given query, providing a score between 0 and 1. In this project, we calculate NDCG@5 to evaluate the top 5 search results for each query.

### Search Query Evaluation

The evaluation process includes:
1. **Query Processing**: Matching queries against document metadata.
2. **Relevance Scoring**: Using true document IDs to calculate relevance scores.
3. **NDCG Calculation**: Aggregating scores to calculate the average relevance.

## Future Enhancements

1. **Parallel Processing**: Optimize data loading and evaluation functions for concurrent processing.
2. **Extended Metrics**: Add other evaluation metrics like Mean Reciprocal Rank (MRR).
3. **Benchmarking with Larger Datasets**: Test Colivara's scalability with larger data volumes.
4. **Automated Testing**: Integrate unit and integration tests for CI/CD compatibility.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.