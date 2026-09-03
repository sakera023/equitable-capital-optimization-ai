"""Interactive research dashboard for the Equitable Capital Optimization prototype."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from equitable_capital import (
    allocate_capital,
    explain_applicant,
    fairness_audit,
    generate_synthetic_startups,
    global_feature_importance,
    opportunity_gap,
    summarize_allocation,
    train_model,
)

st.set_page_config(
    page_title="Equitable Capital Optimization AI",
    page_icon="📊",
    layout="wide",
)

st.title("AI-Powered Equitable Capital Optimization")
st.caption(
    "Predictive capital-readiness analysis, explainability, structural-access "
    "auditing, and funding-allocation simulation."
)
st.warning(
    "Research and educational use only. Do not use this prototype to make real "
    "credit, lending, investment, or eligibility decisions."
)


@st.cache_data
def load_data() -> pd.DataFrame:
    return generate_synthetic_startups(n=1500, seed=42)


@st.cache_resource
def load_model(data: pd.DataFrame):
    return train_model(data)


data = load_data()
result = load_model(data)
scored = result.scored_data

with st.sidebar:
    st.header("Research controls")
    st.write("Adjust diagnostic and allocation settings for the research simulation.")
    selection_threshold = st.slider(
        "Selection threshold", 0.10, 0.90, 0.50, 0.05
    )
    equity_weight = st.slider("Equity/context weight", 0.0, 0.60, 0.30, 0.05)
    budget = st.number_input(
        "Capital pool ($)",
        min_value=100_000.0,
        max_value=100_000_000.0,
        value=5_000_000.0,
        step=100_000.0,
    )
    st.divider()
    st.caption("Synthetic data • reproducible seed • no API keys required")

tabs = st.tabs(
    [
        "Executive Dashboard",
        "Business Assessment",
        "Fairness Audit",
        "Capital Allocation",
        "Model Details",
    ]
)

with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Businesses", f"{len(scored):,}")
    c2.metric("ROC-AUC", f"{result.metrics['roc_auc']:.3f}")
    c3.metric("F1 Score", f"{result.metrics['f1']:.3f}")
    c4.metric("Avg. Readiness", f"{scored['capital_readiness_score'].mean():.1f}/100")

    fig = px.scatter(
        scored,
        x="requested_capital",
        y="capital_readiness_score",
        color="underserved_context_index",
        hover_data=["startup_id", "state", "industry"],
        title="Capital Need vs. Predicted Capital Readiness",
        labels={
            "underserved_context_index": "Structural Barrier Index",
            "requested_capital": "Requested Capital ($)",
            "capital_readiness_score": "Capital Readiness Score",
        },
    )
    st.plotly_chart(fig, use_container_width=True)

    state_summary = scored.groupby("state", as_index=False).agg(
        avg_readiness=("capital_readiness_score", "mean"),
        avg_barrier_index=("underserved_context_index", "mean"),
        businesses=("startup_id", "count"),
    )
    st.subheader("State-level synthetic summary")
    st.dataframe(
        state_summary.sort_values("avg_readiness", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

with tabs[1]:
    st.subheader("Synthetic Business Assessment")
    startup_id = st.selectbox("Select a synthetic business", scored["startup_id"].tolist())
    row = scored.loc[scored["startup_id"] == startup_id].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Capital Readiness", f"{row['capital_readiness_score']:.1f}/100")
    c2.metric(
        "Predicted Funding Success",
        f"{100 * row['predicted_success_probability']:.1f}%",
    )
    c3.metric("Structural Barrier Index", f"{row['underserved_context_index']:.2f}")

    explanation = explain_applicant(result.pipeline, row, scored)
    fig = px.bar(
        explanation.head(8),
        x="contribution_proxy",
        y="feature",
        orientation="h",
        title="Local Model Sensitivity",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "This is a directional model-sensitivity explanation and does not establish causality."
    )

with tabs[2]:
    st.subheader("Distributional Fairness / Opportunity Audit")
    audit = fairness_audit(scored, threshold=selection_threshold)
    gap = opportunity_gap(scored)

    c1, c2 = st.columns(2)
    c1.metric("Readiness Gap", f"{gap['readiness_gap_points']:+.2f} points")
    c2.metric("Requested Capital Gap", f"${gap['requested_capital_gap']:,.0f}")

    st.dataframe(
        audit.style.format(
            {
                "selection_rate": "{:.1%}",
                "avg_predicted_success": "{:.1%}",
                "avg_requested_capital": "${:,.0f}",
                "avg_readiness_score": "{:.1f}",
                "selection_rate_ratio": "{:.3f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.info(
        "This audit is a research diagnostic, not a legal determination of fairness, "
        "discrimination, or compliance."
    )

with tabs[3]:
    st.subheader("Capital Allocation Simulation")
    baseline, equitable = allocate_capital(
        scored, budget=budget, equity_weight=equity_weight
    )
    summary = pd.DataFrame(
        [
            {"scenario": "Efficiency-only", **summarize_allocation(baseline, budget)},
            {"scenario": "Equity-aware", **summarize_allocation(equitable, budget)},
        ]
    )

    st.dataframe(
        summary.style.format(
            {
                "capital_allocated": "${:,.0f}",
                "budget_utilization": "{:.1%}",
                "share_to_higher_barrier_contexts": "{:.1%}",
                "expected_successes": "{:.1f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    fig = px.bar(
        summary,
        x="scenario",
        y="share_to_higher_barrier_contexts",
        title="Share of Allocated Capital Reaching Higher-Barrier Contexts",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "Download equity-aware allocation CSV",
        equitable.to_csv(index=False).encode("utf-8"),
        file_name="equity_aware_allocation.csv",
        mime="text/csv",
    )

with tabs[4]:
    st.subheader("Model Performance")
    metric_table = pd.DataFrame(
        [{"metric": name, "value": value} for name, value in result.metrics.items()]
    )
    st.dataframe(metric_table, use_container_width=True, hide_index=True)

    importance = global_feature_importance(result).head(12)
    fig = px.bar(
        importance.sort_values("importance"),
        x="importance",
        y="feature",
        orientation="h",
        title="Top Global Feature Importances",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Feature importance is model-specific and does not imply causality. Metrics are "
        "computed on synthetic holdout data."
    )
