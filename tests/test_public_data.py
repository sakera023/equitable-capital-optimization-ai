import pytest

from equitable_capital.public_data import PUBLIC_DATASETS, _select_xlsx_resource


def test_public_dataset_catalog_uses_sba_sources():
    assert {"sba_state_2025", "sba_metro_2025"}.issubset(PUBLIC_DATASETS)
    for dataset in PUBLIC_DATASETS.values():
        assert dataset["landing_page"].startswith("https://data.sba.gov/")


def test_select_xlsx_resource_prefers_active_excel_resource():
    package = {
        "resources": [
            {"format": "CSV", "url": "https://example.test/data.csv", "state": "active"},
            {"format": "XLSX", "url": "https://example.test/old.xlsx", "state": "deleted"},
            {"format": "XLSX", "url": "https://example.test/current.xlsx", "state": "active"},
        ]
    }

    selected = _select_xlsx_resource(package)

    assert selected["url"] == "https://example.test/current.xlsx"


def test_select_xlsx_resource_rejects_missing_excel_file():
    with pytest.raises(ValueError):
        _select_xlsx_resource(
            {"resources": [{"format": "CSV", "url": "https://example.test/data.csv"}]}
        )
