"""Interactive research dashboard for the Equitable Capital Optimization prototype."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from equitable_capital import (
    PUBLIC_DATASETS,
    allocate_capital,
    explain_applicant,
    fairness_audit,
    generate_synthetic_startups,
    global_feature_importance,
    load_sba_public_workbook,
    opportunity_gap,
    prepare_public_state_map,
    public_state_metric_options,
    summarize_allocation,
    summarize_synthetic_states,
    train_model,
)

PUBLICATION_URL = (
    "https://www.researchgate.net/publication/"
    "410866072_An_AI-Powered_Framework_for_Equitable_Capital_Optimization_"
    "Leveraging_Predictive_Intelligence_to_Empower_Underserved_"
    "Entrepreneurial_Ecosystems_in_the_US"
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

link_github, link_pypi, link_publication = st.columns(3)
with link_github:
    st.link_button(
        "GitHub Repository",
        "https://github.com/sakera023/equitable-capital-optimization-ai",
        use_container_width=True,
    )
with link_pypi:
    st.link_button(
        "Python Package (PyPI)",
        "https://pypi.org/project/equitable-capital-optimization-ai/",
        use_container_width=True,
    )
with link_publication:
    st.link_button(
        "Related Publication",
        PUBLICATION_URL,
        use_container_width=True,
    )


@st.cache_data
def load_data() -> pd.DataFrame:
    return generate_synthetic_startups(n=1500, seed=42)


@st.cache_resource
def load_model(data: pd.DataFrame):
    return train_model(data)


@st.cache_data(ttl=3600, show_spinner=False)
def load_public_workbook(dataset_key: str):
    return load_sba_public_workbook(dataset_key)


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
    st.caption(
        "Synthetic model • optional official SBA public data • no API key required"
    )

tabs = st.tabs(
    [
        "Executive Dashboard",
        "Geographic Insights",
        "Business Assessment",
        "Fairness Audit",
        "Capital Allocation",
        "U.S. Public Data",
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
    st.subheader("Geographic Research View")
    st.write(
        "Explore state-level patterns in the synthetic research dataset. "
        "These maps visualize model outputs and contextual indicators; they are "
        "not measurements of real state economic performance."
    )

    state_geo = summarize_synthetic_states(scored)
    geo_metric_options = {
        "Average Capital Readiness": "avg_readiness",
        "Average Structural Barrier Index": "avg_barrier_index",
        "Average Requested Capital": "avg_requested_capital",
        "Average Predicted Funding Success": "avg_predicted_success",
        "Synthetic Business Count": "businesses",
    }
    geo_label = st.selectbox(
        "Map metric",
        list(geo_metric_options),
        key="synthetic_geo_metric",
    )
    geo_metric = geo_metric_options[geo_label]

    geo_fig = px.choropleth(
        state_geo,
        locations="state",
        locationmode="USA-states",
        color=geo_metric,
        scope="usa",
        hover_name="state_name",
        hover_data={
            "state": False,
            "avg_readiness": ":.1f",
            "avg_barrier_index": ":.3f",
            "avg_requested_capital": ":,.0f",
            "avg_predicted_success": ":.1%",
            "businesses": ":,",
        },
        title=f"Synthetic State-Level Map — {geo_label}",
        labels={
            "avg_readiness": "Avg. readiness",
            "avg_barrier_index": "Avg. barrier index",
            "avg_requested_capital": "Avg. requested capital",
            "avg_predicted_success": "Avg. predicted success",
            "businesses": "Synthetic businesses",
        },
    )
    geo_fig.update_layout(margin={"r": 0, "t": 55, "l": 0, "b": 0})
    st.plotly_chart(geo_fig, use_container_width=True)
    st.caption(
        "Only states represented in the synthetic generator are colored. "
        "Use the U.S. Public Data tab for official nationwide aggregate statistics."
    )

    st.dataframe(
        state_geo.sort_values(geo_metric, ascending=False),
        use_container_width=True,
        hide_index=True,
    )

with tabs[2]:
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

with tabs[3]:
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

with tabs[4]:
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

with tabs[5]:
    st.subheader("Official U.S. Small Business Data")
    st.write(
        "Browse authoritative aggregate datasets from the U.S. Small Business "
        "Administration Office of Advocacy. These data provide geographic and "
        "economic context and are kept separate from the synthetic prediction model."
    )

    public_options = {
        dataset["label"]: key for key, dataset in PUBLIC_DATASETS.items()
    }
    selected_label = st.selectbox(
        "Choose an official dataset",
        list(public_options),
        key="public_dataset_selector",
    )
    selected_key = public_options[selected_label]
    selected_source = PUBLIC_DATASETS[selected_key]

    st.caption(selected_source["description"])
    st.link_button(
        "Open official SBA dataset page",
        selected_source["landing_page"],
    )

    session_key = f"public_workbook::{selected_key}"
    if st.button("Load official SBA workbook", type="primary"):
        try:
            with st.spinner("Loading the current official SBA workbook..."):
                st.session_state[session_key] = load_public_workbook(selected_key)
        except Exception as exc:
            st.error(
                "The public dataset could not be loaded right now. "
                f"Source error: {exc}"
            )

    if session_key in st.session_state:
        metadata, public_sheets = st.session_state[session_key]

        st.success("Official SBA data loaded.")
        st.markdown(
            f"**Publisher:** U.S. Small Business Administration, Office of Advocacy  \\n"
            f"**Dataset:** {metadata['package_title']}  \\n"
            f"**Last catalog update:** {metadata['last_modified'] or 'Not reported'}  \\n"
            f"**License:** {metadata['license_title']}"
        )

        public_sheet_name = st.selectbox(
            "Workbook sheet",
            list(public_sheets),
            key=f"public_sheet::{selected_key}",
        )
        public_frame = public_sheets[public_sheet_name]
        st.dataframe(
            public_frame.head(2000),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            f"Showing up to 2,000 rows from {len(public_frame):,} rows in this sheet."
        )

        if selected_key == "sba_state_2025":
            state_column, map_metrics = public_state_metric_options(public_frame)
            if state_column and map_metrics:
                st.subheader("Official SBA State Map")
                public_metric = st.selectbox(
                    "Choose a state-level measure to map",
                    map_metrics,
                    key=f"public_map_metric::{selected_key}::{public_sheet_name}",
                )
                try:
                    public_map = prepare_public_state_map(
                        public_frame,
                        metric_column=public_metric,
                        state_column=state_column,
                    )
                    public_fig = px.choropleth(
                        public_map,
                        locations="state",
                        locationmode="USA-states",
                        color="value",
                        scope="usa",
                        hover_name="state_name",
                        title=f"Official SBA State Map — {public_metric}",
                        labels={"value": public_metric},
                    )
                    public_fig.update_layout(
                        margin={"r": 0, "t": 55, "l": 0, "b": 0}
                    )
                    st.plotly_chart(public_fig, use_container_width=True)
                    st.caption(
                        "Map values come from the selected official SBA worksheet. "
                        "If a worksheet contains multiple rows per state, numeric "
                        "values are averaged for visualization."
                    )
                except ValueError as exc:
                    st.info(f"A state map is not available for this measure: {exc}")
            else:
                st.caption(
                    "This worksheet does not contain a detectable state field and "
                    "numeric measure suitable for mapping."
                )

        csv_name = (
            f"{selected_key}_{public_sheet_name}"
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
        )
        st.download_button(
            "Download selected sheet as CSV",
            public_frame.to_csv(index=False).encode("utf-8"),
            file_name=f"{csv_name}.csv",
            mime="text/csv",
        )
        st.info(
            "These aggregate public statistics are provided for contextual research "
            "only. They are not used to train or validate the applicant-level "
            "synthetic capital-readiness model."
        )

with tabs[6]:
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
