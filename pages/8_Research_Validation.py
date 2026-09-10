"""Interactive calibration and robustness diagnostics."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from equitable_capital.calibration import run_calibration_benchmark, summarize_calibration

st.set_page_config(page_title="Research Validation", page_icon="🧪", layout="wide")
st.title("Research Validation & Probability Calibration")
st.caption(
    "Repeated holdout evaluation of uncalibrated, sigmoid-calibrated, and "
    "isotonic-calibrated probability estimates."
)
st.warning(
    "All applicant-level observations and outcomes used on this page are synthetic. "
    "These diagnostics demonstrate research methodology and software behavior; they do "
    "not establish real-world credit, lending, or investment validity."
)


@st.cache_data(show_spinner=False)
def calibration_results():
    results = run_calibration_benchmark()
    return results, summarize_calibration(results)


if st.button("Run repeated calibration benchmark", type="primary"):
    with st.spinner("Running repeated holdout calibration analysis..."):
        results, summary = calibration_results()
        st.session_state["calibration_results"] = (results, summary)

if "calibration_results" in st.session_state:
    results, summary = st.session_state["calibration_results"]

    st.subheader("Calibration summary")
    st.dataframe(summary, use_container_width=True, hide_index=True)

    metric = st.selectbox(
        "Reliability metric",
        ["brier_mean", "ece_mean", "log_loss_mean", "roc_auc_mean"],
        index=0,
    )
    fig = px.bar(
        summary,
        x="method",
        y=metric,
        title=f"Repeated Holdout Calibration — {metric}",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Run-level results")
    st.dataframe(results, use_container_width=True, hide_index=True)
    st.download_button(
        "Download calibration runs (CSV)",
        results.to_csv(index=False).encode("utf-8"),
        file_name="calibration_runs.csv",
        mime="text/csv",
    )

    st.info(
        "Lower Brier score, log loss, and expected calibration error indicate stronger "
        "probability reliability within this synthetic experiment. ROC-AUC measures "
        "ranking discrimination and should be interpreted separately."
    )
else:
    st.info(
        "Run the benchmark to compare probability reliability across calibration methods."
    )

st.divider()
st.markdown(
    "Methodology: [docs/CALIBRATION.md]"
    "(https://github.com/sakera023/equitable-capital-optimization-ai/blob/main/"
    "docs/CALIBRATION.md)"
)
