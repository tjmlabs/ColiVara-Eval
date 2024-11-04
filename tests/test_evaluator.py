import pytest
from src.evaluator import dcg, ndcg_at_k, evaluate_rag_model
import pandas as pd


class MockResult:
    def __init__(self, document_name):
        self.document_name = document_name


class MockClient:
    def search(self, query, collection_name, top_k):
        # Mock search results
        return MockSearchResults()


class MockSearchResults:
    def __init__(self):
        self.results = [MockResult("1"), MockResult("2"), MockResult("3")]


def test_dcg():
    scores = [3, 2, 3, 0, 1, 2]
    assert dcg(scores) == pytest.approx(6.861, 0.001)


def test_ndcg_at_k():
    results = [MockResult("1"), MockResult("2"), MockResult("3")]
    true_doc_id = 1
    assert ndcg_at_k(results, true_doc_id, k=3) == 1.0

    true_doc_id = 2
    assert ndcg_at_k(results, true_doc_id, k=3) == pytest.approx(0.6309, 0.001)


def test_evaluate_rag_model():
    # Mocked data for queries and expected true document IDs
    queries_data = {"query": ["query1", "query2"], "id": [1, 2]}
    queries_df = pd.DataFrame(queries_data)

    # Instantiate the mock client
    client = MockClient()
    collection_name = "test_collection"

    # Evaluate using the RAG model evaluator
    mean_ndcg, ndcg_scores = evaluate_rag_model(
        queries_df, client, collection_name, top_k=3
    )

    # Check mean NDCG score
    assert mean_ndcg == pytest.approx(0.8154, 0.001)

    # Additional check: Verify individual NDCG scores if needed
    # Here assuming expected individual scores based on mocked search results
    assert len(ndcg_scores) == len(queries_df)
    assert ndcg_scores[0] == 1.0
    assert ndcg_scores[1] == pytest.approx(0.6309, 0.001)
