import numpy as np

from app.services.query_service import cited_numbers
from app.services.retriever import cosine_scores, top_indices


def test_cosine_identical_opposite_and_orthogonal():
    matrix = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0]])
    scores = cosine_scores(matrix, np.array([1.0, 0.0]))
    assert np.allclose(scores, [1.0, -1.0, 0.0])


def test_cosine_ignores_vector_length():
    matrix = np.array([[2.0, 2.0], [10.0, 10.0]])
    scores = cosine_scores(matrix, np.array([1.0, 1.0]))
    assert np.allclose(scores, [1.0, 1.0])


def test_cosine_handles_zero_vector():
    scores = cosine_scores(np.array([[0.0, 0.0]]), np.array([1.0, 0.0]))
    assert np.allclose(scores, [0.0])


def test_top_indices_orders_and_limits():
    scores = np.array([0.2, 0.9, 0.5, 0.7])
    assert top_indices(scores, top_k=2, min_score=0.0) == [1, 3]


def test_top_indices_applies_min_score():
    scores = np.array([0.2, 0.9, 0.1])
    assert top_indices(scores, top_k=5, min_score=0.25) == [1]


def test_cited_numbers_dedupes_and_drops_out_of_range():
    answer = "Dentist on 24 Nov [2]. Clinic is Apollo [2][1]. Also [7]."
    assert cited_numbers(answer, max_number=3) == [2, 1]
