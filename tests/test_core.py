from core import (
    allocate_capital,
    fairness_audit,
    generate_synthetic_startups,
    train_model,
)

def test_generation():
    df = generate_synthetic_startups(200, seed=7)
    assert len(df) == 200
    assert df["underserved_context_index"].between(0, 1).all()

def test_model_probabilities():
    df = generate_synthetic_startups(400, seed=9)
    result = train_model(df)
    assert result.scored_data["predicted_success_probability"].between(0, 1).all()
    assert 0 <= result.auc <= 1
    assert 0 <= result.accuracy <= 1

def test_fairness_audit():
    df = generate_synthetic_startups(400, seed=11)
    result = train_model(df)
    audit = fairness_audit(result.scored_data)
    assert audit["selection_rate"].between(0, 1).all()

def test_allocation_budget():
    df = generate_synthetic_startups(400, seed=13)
    result = train_model(df)
    baseline, equitable = allocate_capital(result.scored_data, 500000)
    assert baseline["allocated_capital"].sum() <= 500000 + 1e-6
    assert equitable["allocated_capital"].sum() <= 500000 + 1e-6
