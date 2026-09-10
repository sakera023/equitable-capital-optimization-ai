from io import BytesIO

import pandas as pd

from equitable_capital.cdfi import (
    discover_cdfi_workbook_url,
    load_cdfi_certification_workbook,
    summarize_cdfi_by_state,
)


def test_discover_cdfi_workbook_url_uses_official_link():
    html = (
        b'<a href="/media/123456/download?inline=">'
        b'List of Currently Certified CDFIs</a>'
    )
    url = discover_cdfi_workbook_url(fetch_bytes=lambda _: html)
    assert url == "https://www.cdfifund.gov/media/123456/download?inline="


def test_loader_prefers_institution_roster_over_state_summary():
    summary = pd.DataFrame({"State": ["VA", "MD", "TX"], "Count": [20, 10, 30]})
    detail = pd.DataFrame(
        {
            "Organization Name": [f"CDFI {index}" for index in range(120)],
            "State": ["VA", "MD", "TX", "CA"] * 30,
            "Organization Type": ["Loan Fund"] * 120,
        }
    )
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="State Summary", index=False)
        detail.to_excel(writer, sheet_name="List of Certified CDFIs", index=False)

    workbook = buffer.getvalue()
    landing = b'<a href="/media/123456/download?inline=">List of Currently Certified CDFIs</a>'

    def fake_fetch(url):
        if "certification/cdfi" in url:
            return landing
        return workbook

    metadata, frame = load_cdfi_certification_workbook(fetch_bytes=fake_fetch)

    assert metadata["worksheet"] == "List of Certified CDFIs"
    assert len(frame) == 120


def test_cdfi_state_summary_counts_unique_institutions():
    frame = pd.DataFrame(
        {
            "Organization Name": ["A", "A", "B", "C"],
            "State": ["Virginia", "VA", "Maryland", "Texas"],
            "Organization Type": ["Loan Fund", "Loan Fund", "Bank", "Credit Union"],
        }
    )
    summary = summarize_cdfi_by_state(frame)

    va = summary.loc[summary["state"] == "VA"].iloc[0]
    assert va["certified_cdfis"] == 1
    assert va["institution_type_count"] == 1
