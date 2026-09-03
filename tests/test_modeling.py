from equitable_capital import (
    generate_synthetic_startups,
    global_feature_importance,
    train_model,
)


def test_model_probabilities_and_metrics():
    data = generate_synthetic_startups(500, seed=10)
    result = train_model(data)

    assert result.scored_data["predicted_success_probability"].between(0, 1).all()
    for metric in ["roc_auc", "accuracy", "precision", "recall", "f1", "brier"]:
        assert 0 <= result.metrics[metric] <= 1


def test_feature_importance_sums_to_one():
    data = generate_synthetic_startups(500, seed=11)
    result = train_model(data)
    importance = global_feature_importance(result)

    assert not importance.empty
    assert abs(float(importance["importance"].sum()) - 1.0) < 1e-9
