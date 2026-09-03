import pandas as pd
import plotly.express as px
import streamlit as st

from core import (
    allocate_capital,
    explain_applicant,
    fairness_audit,
    generate_synthetic_startups,
    summarize_allocation,
    train_model,
)

st.set_page_config(
    page_title="Equitable Capital Optimization AI",
    page_icon="📊",
    layout="wide",
)

@st.cache_data
def load_data():
    return generate_synthetic_startups(n=1500, seed=42)

@st.cache_resource
def load_model(data):
    return train_model(data)

data = load_data()
result = load_model(data)
scored = result.scored_data

st.title("AI-Powered Framework for Equitable Capital Optimization")
st.caption(
    "Predictive capital-readiness analysis, explainability, structural-access "
    "auditing, and equitable funding-allocation simulation."
)
st.warning(
    "Research and educational use only. Do not use this prototype to make real "
    "credit, lending, investment, or eligibility decisions."
)

tab1, tab2, tab3, tab4 = st.tabs([
    "Executive Dashboard",
    "Business Assessment",
    "Fairness Audit",
    "Capital Allocation",
])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Businesses", f"{len(scored):,}")
    c2.metric("Model ROC-AUC", f"{result.auc:.3f}")
    c3.metric("Model Accuracy", f"{result.accuracy:.3f}")
    c4.metric("Average Readiness", f"{scored['capital_readiness_score'].mean():.1f}/100")

    fig = px.scatter(
        scored,
        x="requested_capital",
        y="capital_readiness_score",
        color="underserved_context_index",
        hover_data=["startup_id", "state", "industry"],
        title="Capital Need vs. Predicted Capital Readiness",
        labels={"underserved_context_index": "Structural Barrier Index"},
    )
    st.plotly_chart(fig, use_container_width=True)

    state_summary = scored.groupby("state", as_index=False).agg(
        avg_readiness=("capital_readiness_score", "mean"),
        avg_barrier_index=("underserved_context_index", "mean"),
        businesses=("startup_id", "count"),
    )
    st.dataframe(
        state_summary.sort_values("avg_readiness", ascending=False),
        use_container_width=True,
    )

with tab2:
    st.subheader("Synthetic Business Assessment")
    startup_id = st.selectbox("Select a business", scored["startup_id"].tolist())
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
        "This is a model sensitivity explanation. It does not establish causality."
    )

with tab3:
    st.subheader("Distributional Fairness / Opportunity Audit")
    threshold = st.slider("Selection threshold", 0.10, 0.90, 0.50, 0.05)
    audit = fairness_audit(scored, threshold=threshold)

    st.dataframe(
        audit.style.format({
            "selection_rate": "{:.1%}",
            "avg_predicted_success": "{:.1%}",
            "avg_requested_capital": "${:,.0f}",
            "avg_readiness_score": "{:.1f}",
            "selection_rate_ratio": "{:.3f}",
        }),
        use_container_width=True,
    )

    st.info(
        "The audit compares structural-access contexts and is a research diagnostic, "
        "not a legal determination of fairness or discrimination."
    )

with tab4:
    st.subheader("Equitable Capital Allocation Simulation")
    budget = st.number_input(
        "Total capital pool ($)",
        min_value=100000.0,
        max_value=100000000.0,
        value=5000000.0,
        step=100000.0,
    )
    equity_weight = st.slider(
        "Equity/context weight",
        min_value=0.0,
        max_value=0.60,
        value=0.30,
        step=0.05,
    )

    baseline, equitable = allocate_capital(scored, budget, equity_weight)
    baseline_summary = summarize_allocation(baseline, budget)
    equitable_summary = summarize_allocation(equitable, budget)

    summary = pd.DataFrame([
        {"scenario": "Efficiency-only", **baseline_summary},
        {"scenario": "Equity-aware", **equitable_summary},
    ])

    st.dataframe(
        summary.style.format({
            "capital_allocated": "${:,.0f}",
            "budget_utilization": "{:.1%}",
            "share_to_higher_barrier_contexts": "{:.1%}",
            "expected_successes": "{:.1f}",
        }),
        use_container_width=True,
    )

    fig = px.bar(
        summary,
        x="scenario",
        y="share_to_higher_barrier_contexts",
        title="Allocated Capital Reaching Higher-Barrier Contexts",
    )
    st.plotly_chart(fig, use_container_width=True)
