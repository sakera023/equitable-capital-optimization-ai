"""Authoritative public U.S. small-business data access helpers.

The predictive prototype continues to use synthetic records. These helpers expose
official SBA Office of Advocacy datasets as contextual research evidence and do
not mix public aggregate statistics into the applicant-level prediction model.
"""

from __future__ import annotations

import json
from io import BytesIO
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

SBA_CKAN_PACKAGE_SHOW = "https://data.sba.gov/api/3/action/package_show"

PUBLIC_DATASETS = {
    "sba_state_2025": {
        "label": "SBA State Small Business Statistics 2025",
        "slug": "state-small-business-statistics-2025",
        "landing_page": "https://data.sba.gov/dataset/state-small-business-statistics-2025",
        "description": (
            "State-level small-business statistics from the U.S. Small Business "
            "Administration Office of Advocacy, including employment, job creation, "
            "and other profile indicators."
        ),
    },
    "sba_metro_2025": {
        "label": "SBA Metropolitan Area Small Business Statistics 2025",
        "slug": "metropolitan-area-small-business-statistics-2025",
        "landing_page": (
            "https://data.sba.gov/dataset/"
            "metropolitan-area-small-business-statistics-2025"
        ),
        "description": (
            "Metropolitan-area small-business statistics from the U.S. Small Business "
            "Administration Office of Advocacy."
        ),
    },
}


def _fetch_bytes(url: str, timeout: int = 30) -> bytes:
    request = Request(
        url,
        headers={"User-Agent": "equitable-capital-optimization-ai/0.3 (+research)"},
    )
    with urlopen(request, timeout=timeout) as response:  # noqa: S310
        return response.read()


def _fetch_json(url: str, timeout: int = 30) -> dict:
    return json.loads(_fetch_bytes(url, timeout=timeout).decode("utf-8"))


def _select_xlsx_resource(package: dict) -> dict:
    resources = package.get("resources", [])
    candidates = [
        resource
        for resource in resources
        if str(resource.get("format", "")).strip().lower() in {"xlsx", "xls"}
        and resource.get("url")
    ]
    if not candidates:
        raise ValueError("No Excel resource was found for the selected SBA dataset.")

    active = [
        resource
        for resource in candidates
        if str(resource.get("state", "active")).lower() == "active"
    ]
    return (active or candidates)[0]


def get_sba_dataset_metadata(dataset_key: str) -> dict:
    """Resolve live SBA CKAN metadata for one supported public dataset."""
    if dataset_key not in PUBLIC_DATASETS:
        raise KeyError(f"Unknown public dataset: {dataset_key}")

    catalog_entry = PUBLIC_DATASETS[dataset_key]
    query = urlencode({"id": catalog_entry["slug"]})
    payload = _fetch_json(f"{SBA_CKAN_PACKAGE_SHOW}?{query}")

    if not payload.get("success"):
        raise RuntimeError("The SBA data catalog did not return a successful response.")

    package = payload["result"]
    resource = _select_xlsx_resource(package)
    return {
        "key": dataset_key,
        "label": catalog_entry["label"],
        "description": catalog_entry["description"],
        "landing_page": catalog_entry["landing_page"],
        "package_title": package.get("title", catalog_entry["label"]),
        "package_notes": package.get("notes", ""),
        "last_modified": package.get("metadata_modified") or package.get("revision_timestamp"),
        "resource_name": resource.get("name") or resource.get("description") or "Excel resource",
        "resource_url": resource["url"],
        "resource_format": resource.get("format", "XLSX"),
        "license_title": package.get("license_title") or "U.S. Government Works",
    }


def load_sba_public_workbook(dataset_key: str) -> tuple[dict, dict[str, pd.DataFrame]]:
    """Download one official SBA workbook and return metadata plus all sheets."""
    metadata = get_sba_dataset_metadata(dataset_key)
    workbook_bytes = _fetch_bytes(metadata["resource_url"])
    sheets = pd.read_excel(BytesIO(workbook_bytes), sheet_name=None)

    cleaned = {
        str(sheet_name): frame.dropna(axis=0, how="all").dropna(axis=1, how="all")
        for sheet_name, frame in sheets.items()
    }
    cleaned = {name: frame for name, frame in cleaned.items() if not frame.empty}
    if not cleaned:
        raise ValueError("The selected SBA workbook did not contain a readable data sheet.")

    return metadata, cleaned
