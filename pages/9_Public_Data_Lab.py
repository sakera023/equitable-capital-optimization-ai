"""Authoritative public-data research page."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from equitable_capital.cdfi import (
    CDFI_CERTIFICATION,
    load_cdfi_certification_workbook,
    summarize_cdfi_by_state,
)
from equitable_capital.census_abs import (
    ABS_2022_COMPANY_SUMMARY,
    load_abs_state_data,
    total_population_rows,
)
from equitable_capital.census_cbp import (
    CENSUS_CBP_2023,
    STATE_ABBR_TO_FIPS,
    county_name_lookup,
    load_cbp_county_file,
    load_county_geojson,
    summarize_cbp_county_totals,
    summarize_county_industry_concentration,
)

st.set_page_config(page_title="Public Data Lab", page_icon="🗺️", layout="wide")
st.title("U.S. Public Data Lab")
st.caption(
    "Authoritative Census and CDFI Fund context kept methodologically separate from the "
    "synthetic applicant-level prediction model."
)
st.warning(
    "Public geographic indicators are descriptive. They do not establish applicant-level "
    "creditworthiness, causal capital constraints, discrimination, or lending outcomes."
)

county_tab, cdfi_tab, abs_tab = st.tabs(
    ["Census CBP County", "Certified CDFIs", "Census ABS"]
)


@st.cache_data(ttl=86400, show_spinner=False)
def cached_cbp_county():
    raw = load_cbp_county_file()
    totals = summarize_cbp_county_totals(raw)
    concentration = summarize_county_industry_concentration(raw)
    return totals.merge(concentration, on="geoid", how="left")


@st.cache_data(ttl=86400, show_spinner=False)
def cached_county_geojson(state_fips: str):
    return load_county_geojson(state_fips)


@st.cache_data(ttl=86400, show_spinner=False)
def cached_cdfi():
    metadata, raw = load_cdfi_certification_workbook()
    return metadata, summarize_cdfi_by_state(raw)


with county_tab:
    st.subheader("County Business Patterns 2023")
    st.write(CENSUS_CBP_2023["description"])
    st.link_button("Open official Census CBP source", CENSUS_CBP_2023["landing_page"])

    if st.button("Load official Census county data", type="primary", key="load_cbp"):
        try:
            with st.spinner("Downloading and validating Census County Business Patterns..."):
                st.session_state["cbp_county"] = cached_cbp_county()
        except Exception as exc:
            st.error(f"Census CBP data could not be loaded: {exc}")

    if "cbp_county" in st.session_state:
        county = st.session_state["cbp_county"]
        state = st.selectbox(
            "State",
            sorted(county["state"].dropna().unique()),
            index=sorted(county["state"].dropna().unique()).index("VA")
            if "VA" in set(county["state"].dropna())
            else 0,
        )
        state_rows = county[county["state"] == state].copy()
        metric_options = {
            "Establishments": "establishments",
            "Employment": "employment",
            "Annual payroll ($000s)": "annual_payroll_thousands",
            "First-quarter payroll ($000s)": "q1_payroll_thousands",
            "Industry concentration HHI": "industry_hhi",
            "Top-sector share": "top_sector_share",
        }
        available = {
            label: column
            for label, column in metric_options.items()
            if column in state_rows.columns
        }
        metric_label = st.selectbox("County metric", list(available))
        metric = available[metric_label]

        try:
            state_fips = STATE_ABBR_TO_FIPS[state]
            geojson = cached_county_geojson(state_fips)
            labels = county_name_lookup(geojson)
            state_rows["county_name"] = state_rows["geoid"].map(labels).fillna(state_rows["geoid"])

            fig = px.choropleth(
                state_rows,
                geojson=geojson,
                locations="geoid",
                featureidkey="properties.GEOID",
                color=metric,
                hover_name="county_name",
                hover_data={"geoid": True, metric: ":,.2f"},
                title=f"{state} County Business Context — {metric_label}",
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r": 0, "t": 55, "l": 0, "b": 0})
            st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:
            st.info(f"County geometry is temporarily unavailable: {exc}")

        st.dataframe(
            state_rows.sort_values(metric, ascending=False),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download selected state's county context (CSV)",
            state_rows.to_csv(index=False).encode("utf-8"),
            file_name=f"cbp_2023_{state.lower()}_county_context.csv",
            mime="text/csv",
        )
        st.caption(
            "Industry HHI is based on high-level sector establishment shares and is a "
            "business-structure measure, not a measure of lender competition."
        )

with cdfi_tab:
    st.subheader("Current Certified CDFI Organization Geography")
    st.write(CDFI_CERTIFICATION["description"])
    st.link_button("Open official CDFI Fund source", CDFI_CERTIFICATION["landing_page"])

    if st.button("Load current Certified CDFI list", type="primary", key="load_cdfi"):
        try:
            with st.spinner("Loading the current official Certified CDFI workbook..."):
                st.session_state["cdfi_state"] = cached_cdfi()
        except Exception as exc:
            st.error(f"Certified CDFI data could not be loaded: {exc}")

    if "cdfi_state" in st.session_state:
        metadata, cdfi_state = st.session_state["cdfi_state"]
        c1, c2 = st.columns(2)
        c1.metric("States / DC represented", f"{cdfi_state['state'].nunique():,}")
        c2.metric("Certified organizations", f"{int(cdfi_state['certified_cdfis'].sum()):,}")
        st.caption(f"Workbook sheet selected: {metadata['worksheet']}")

        fig = px.choropleth(
            cdfi_state,
            locations="state",
            locationmode="USA-states",
            color="certified_cdfis",
            scope="usa",
            hover_name="state_name",
            title="Certified CDFI Organization Locations by State",
            labels={"certified_cdfis": "Certified CDFIs"},
        )
        fig.update_layout(margin={"r": 0, "t": 55, "l": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(cdfi_state, use_container_width=True, hide_index=True)
        st.info(
            "An institution's listed state does not equal lending volume, target-market "
            "coverage, branch presence, or capital received by businesses in that state."
        )

with abs_tab:
    st.subheader("Annual Business Survey 2022 — Company Summary")
    st.write(
        "Query official Census ABS aggregate employer-firm data. Census currently requires "
        "an API key, which is used only for this request and is not stored by the app."
    )
    st.link_button(
        "Open official Census ABS documentation",
        ABS_2022_COMPANY_SUMMARY["documentation"],
    )
    api_key = st.text_input("Census API key", type="password", key="abs_api_key")

    if st.button("Load state-level ABS data", type="primary", key="load_abs"):
        try:
            with st.spinner("Querying the official Census ABS API..."):
                metadata, frame = load_abs_state_data(api_key=api_key)
                st.session_state["abs_state"] = (metadata, frame)
        except Exception as exc:
            st.error(f"Census ABS data could not be loaded: {exc}")

    if "abs_state" in st.session_state:
        metadata, frame = st.session_state["abs_state"]
        st.success(f"Loaded official ABS {metadata['reference_year']} state-level rows.")
        st.dataframe(frame.head(3000), use_container_width=True, hide_index=True)
        st.caption(f"Showing up to 3,000 of {len(frame):,} returned rows.")

        total_rows = total_population_rows(frame)
        if not total_rows.empty and "state" in total_rows.columns:
            metric_candidates = [
                column
                for column in ("FIRMPDEMP", "EMP", "RCPPDEMP", "PAYANN")
                if column in total_rows.columns
            ]
            metric = st.selectbox("Explicit-total ABS measure", metric_candidates)
            state_map = total_rows.copy()
            state_map["state_fips"] = state_map["state"].astype(str).str.zfill(2)
            fips_to_abbr = {value: key for key, value in STATE_ABBR_TO_FIPS.items()}
            state_map["state_abbr"] = state_map["state_fips"].map(fips_to_abbr)
            state_map = state_map.dropna(subset=["state_abbr"])
            if not state_map.empty:
                fig = px.choropleth(
                    state_map,
                    locations="state_abbr",
                    locationmode="USA-states",
                    color=metric,
                    scope="usa",
                    hover_name="NAME" if "NAME" in state_map.columns else None,
                    title=f"ABS Explicit-Total State Context — {metric}",
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(
                "No safely identifiable all-population rows were found from the returned "
                "labels. The app will not infer demographic total codes or sum overlapping "
                "categories. Use the raw table for documented subgroup analysis."
            )

        st.download_button(
            "Download returned ABS rows (CSV)",
            frame.to_csv(index=False).encode("utf-8"),
            file_name="census_abs_2022_state_rows.csv",
            mime="text/csv",
        )

st.divider()
st.caption(
    "Public-data layers are contextual research evidence and are deliberately not used as "
    "individual credit, lending, investment, or eligibility inputs."
)
