import pandas as pd
import pytest

from equitable_capital import generate_synthetic_startups


def test_generation_is_reproducible():
    first = generate_synthetic_startups(200, seed=7)
    second = generate_synthetic_startups(200, seed=7)
    pd.testing.assert_frame_equal(first, second)


def test_structural_index_is_bounded():
    data = generate_synthetic_startups(200, seed=8)
    assert data["underserved_context_index"].between(0, 1).all()


def test_small_sample_is_rejected():
    with pytest.raises(ValueError):
        generate_synthetic_startups(50, seed=9)
