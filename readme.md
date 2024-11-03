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

### Evaluation

The main script, `main.py`, initiates the document upsertion process and evaluates the RAG model on Colivara. It requires two arguments: `--collection_name` to specify the target collection and `--n_rows` to define the number of rows to load from the dataset for testing.

Example:
```bash
python main.py --collection_name test_collection --n_rows 100
```

- **`--collection_name`**: The name of the collection to upsert documents into. If the collection doesn't exist, it will be created.
- **`--n_rows`**: The number of rows to load from the dataset. This allows for flexible testing with subsets of data.

The output will include the total number of documents upserted and the average NDCG@5 score for the queries in the dataset, providing insight into the relevance of the search results returned by Colivara.

### Running Collection Manager

The `collection_manager.py` script provides utilities to list and delete collections within Colivara. This script uses argparse to specify the operation (`--list` or `--delete`) and the collection name to delete, if applicable.

#### List Collections
To list all existing collections:
```bash
python collection_manager.py --list
```

#### Delete a Collection
To delete a specific collection, use the `--delete` flag followed by the collection name:
```bash
python collection_manager.py --delete test_collection
```

- **`--delete`**: Specifies the collection name to delete. Ensure that you have the correct collection name, as this action is irreversible.


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