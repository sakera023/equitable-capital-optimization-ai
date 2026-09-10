import pytest

from equitable_capital.census_abs import (
    build_abs_query_url,
    load_abs_county_data,
    parse_census_api_payload,
    total_population_rows,
)


def test_abs_query_requires_runtime_api_key(monkeypatch):
    monkeypatch.delenv("CENSUS_API_KEY", raising=False)
    with pytest.raises(ValueError, match="Census API key"):
        build_abs_query_url(api_key=None)


def test_abs_query_builds_official_state_request():
    url = build_abs_query_url(
        geography="state:*",
        fields=("NAME", "FIRMPDEMP"),
        api_key="example-key",
    )

    assert url.startswith("https://api.census.gov/data/2022/abscs?")
    assert "NAICS2022=00" in url
    assert "key=example-key" in url
    assert "state%3A%2A" in url


def test_parse_census_payload_types_numeric_fields():
    payload = [
        ["NAME", "FIRMPDEMP", "EMP", "state"],
        ["Virginia", "1000", "5000", "51"],
        ["Maryland", "800", "4000", "24"],
    ]
    frame = parse_census_api_payload(payload)

    assert frame.loc[0, "FIRMPDEMP"] == 1000
    assert frame.loc[1, "EMP"] == 4000


def test_county_loader_builds_geoid_and_preserves_metadata():
    payload = [
        ["NAME", "FIRMPDEMP", "state", "county"],
        ["Arlington County, Virginia", "100", "51", "013"],
    ]
    seen = {}

    def fake_fetch(url):
        seen["url"] = url
        return payload

    metadata, frame = load_abs_county_data(
        "51",
        api_key="example-key",
        fields=("NAME", "FIRMPDEMP"),
        fetch_json=fake_fetch,
    )

    assert metadata["geography"] == "county"
    assert frame.loc[0, "geoid"] == "51013"
    assert "county%3A%2A" in seen["url"]
    assert "state%3A51" in seen["url"]


def test_total_population_rows_requires_explicit_total_labels():
    frame = parse_census_api_payload(
        [
            ["NAME", "SEX_LABEL", "ETH_GROUP_LABEL", "FIRMPDEMP", "state"],
            ["Virginia", "Total", "Total", "1000", "51"],
            ["Virginia", "Female", "Total", "400", "51"],
        ]
    )
    total = total_population_rows(frame)

    assert len(total) == 1
    assert total.loc[0, "FIRMPDEMP"] == 1000
