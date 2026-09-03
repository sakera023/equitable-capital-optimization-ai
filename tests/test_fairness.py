from equitable_capital import fairness_audit, generate_synthetic_startups, train_model


def test_fairness_audit_outputs_valid_rates():
    data = generate_synthetic_startups(500, seed=12)
    result = train_model(data)
    audit = fairness_audit(result.scored_data)

    assert audit["selection_rate"].between(0, 1).all()
    assert audit["selection_rate_ratio"].between(0, 1).all()


def test_threshold_changes_selection_rate():
    data = generate_synthetic_startups(500, seed=13)
    result = train_model(data)

    low = fairness_audit(result.scored_data, threshold=0.30)
    high = fairness_audit(result.scored_data, threshold=0.70)
    assert low["selection_rate"].mean() >= high["selection_rate"].mean()
