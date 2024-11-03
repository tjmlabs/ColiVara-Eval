import numpy as np
from typing import List, Any
from tqdm import tqdm


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
        1 if result.document_name == str(true_doc_id) else 0 for result in results[:k]
    ]
    dcg_score = dcg(relevance_scores)
    ideal_relevance = sorted(relevance_scores, reverse=True)
    idcg_score = dcg(ideal_relevance) if ideal_relevance else 1
    return dcg_score / idcg_score if idcg_score else 0


def evaluate_rag_model(
    queries_df: Any, client: Any, collection_name: str, top_k: int = 5
) -> float:
    """
    Evaluate a retrieval-augmented generation (RAG) model using NDCG.

    Args:
        queries_df (Any): DataFrame containing queries and true document IDs.
        client (Any): Search client to retrieve results.
        collection_name (str): Name of the collection to search.
        top_k (int, optional): Number of top results to consider. Defaults to 5.

    Returns:
        float: The mean NDCG score for all queries.
    """
    ndcg_scores = []
    for _, query_data in tqdm(
        queries_df.iterrows(), total=len(queries_df), desc="Evaluating"
    ):
        query_text = query_data["query"]
        true_doc_id = query_data["id"]
        results = client.search(
            query=query_text, collection_name=collection_name, top_k=top_k
        )
        ndcg_score = ndcg_at_k(results.results, true_doc_id, k=top_k)
        ndcg_scores.append(ndcg_score)
    return np.mean(ndcg_scores)
