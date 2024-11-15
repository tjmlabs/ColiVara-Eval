import numpy as np
from typing import List, Any, Tuple
from tqdm import tqdm
import time
from tenacity import retry, stop_after_attempt, wait_fixed


def dcg(scores: List[float]) -> float:
    """
    Calculate the Discounted Cumulative Gain (DCG) for a list of relevance scores.

    Args:
        scores (List[float]): List of relevance scores.

    Returns:
        float: The DCG score.
    """
    return sum(rel / np.log2(idx + 2) for idx, rel in enumerate(scores))


def ndcg_at_k(results: List[Any], true_doc_id: int, k: int = 5) -> float:
    """
    Calculate the Normalized Discounted Cumulative Gain (NDCG) at rank k.

    Args:
        results (List[Any]): List of search results.
        true_doc_id (int): The ID of the true document.
        k (int, optional): The rank position to evaluate. Defaults to 5.

    Returns:
        float: The NDCG score at rank k.
    """
    relevance_scores = [
        result.raw_score
        if result.document_metadata["image_file_name"] == str(true_doc_id)
        else 0
        for result in results[:k]
    ]
    dcg_score = dcg(relevance_scores)
    ideal_relevance = sorted(relevance_scores, reverse=True)
    idcg_score = dcg(ideal_relevance) if ideal_relevance else 1
    return dcg_score / idcg_score if idcg_score else 0


@retry(stop=stop_after_attempt(8), wait=wait_fixed(3))
def get_search_results(client: Any, query_text: str, collection_name: str, top_k: int):
    """
    Retrieve search results with retry mechanism.

    Args:
        client (Any): Search client to retrieve results.
        query_text (str): The search query.
        collection_name (str): Name of the collection to search.
        top_k (int): Number of top results to retrieve.

    Returns:
        Any: Search results from the client.
    """
    results = client.search(
        query=query_text, collection_name=collection_name, top_k=top_k
    )
    if len(results.results) < top_k:
        raise ValueError("Insufficient results, retrying...")
    return results


def evaluate_rag_model(
    queries_df: Any,
    client: Any,
    collection_name: str,
    top_k: int = 5,
) -> Tuple[float, List[float]]:
    """
    Evaluate a retrieval-augmented generation (RAG) model using NDCG, with retry logic.

    Args:
        queries_df (Any): DataFrame containing queries and true document IDs.
        client (Any): Search client to retrieve results.
        collection_name (str): Name of the collection to search.
        top_k (int, optional): Number of top results to consider. Defaults to 5.

    Returns:
        Tuple[float, List[float]]: The mean NDCG score and a list of individual NDCG scores for each query.
    """
    ndcg_scores = []
    latencies = []
    for _, query_data in tqdm(
        queries_df.iterrows(), total=len(queries_df), desc="Evaluating"
    ):
        query_text = query_data["query"]
        true_doc_id = query_data["image_filename"]

        try:
            start = time.time()
            results = get_search_results(
                client, query_text, collection_name, top_k=top_k
            )
            end = time.time()
            latencies.append(end - start)
            ndcg_score = ndcg_at_k(results.results, true_doc_id, k=top_k)
        except Exception as e:
            print(f"Failed to retrieve results for query '{query_text}': {e}")
            ndcg_score = 0  # Assign a score of 0 if retrieval fails after retries

        ndcg_scores.append(ndcg_score)

    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    mean_ndcg_score = np.mean(ndcg_scores)
    return mean_ndcg_score, ndcg_scores, avg_latency
