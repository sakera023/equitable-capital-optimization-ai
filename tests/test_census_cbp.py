from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import pytest

from equitable_capital.census_cbp import (
    county_name_lookup,
    load_cbp_county_file,
    load_county_geojson,
    summarize_cbp_county_totals,
    summarize_county_industry_concentration,
)


def _county_zip_bytes() -> bytes:
    frame = pd.DataFrame(
        {
            "FIPSTATE": ["51", "51", "51", "51", "24"],
            "FIPSCTY": ["013", "013", "013", "013", "031"],
            "NAICS": ["------", "54----", "72----", "44-45-", "------"],
            "LFO": ["001"] * 5,
            "EMPSZES": ["001"] * 5,
            "EST": ["100", "40", "35", "25", "80"],
            "EMP": ["1200", "500", "400", "300", "900"],
            "AP": ["70000", "30000", "22000", "18000", "50000"],
            "QP1": ["17000", "7000", "5500", "4500", "12000"],
        }
    )
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("cbp23co.txt", frame.to_csv(index=False))
    return buffer.getvalue()


def test_load_and_summarize_county_totals():
    frame = load_cbp_county_file(fetch_bytes=lambda _: _county_zip_bytes())
    summary = summarize_cbp_county_totals(frame)

    assert set(summary["geoid"]) == {"51013", "24031"}
    assert summary.loc[summary["geoid"] == "51013", "state"].iloc[0] == "VA"
    assert summary.loc[summary["geoid"] == "51013", "establishments"].iloc[0] == 100


def test_county_industry_hhi_uses_sector_shares():
    frame = load_cbp_county_file(fetch_bytes=lambda _: _county_zip_bytes())
    concentration = summarize_county_industry_concentration(frame)
    row = concentration.loc[concentration["geoid"] == "51013"].iloc[0]

    assert row["sector_count"] == 3
    assert row["industry_hhi"] == pytest.approx((0.4**2 + 0.35**2 + 0.25**2) * 10000)
    assert row["top_sector_share"] == pytest.approx(0.4)


def test_county_geojson_query_and_names():
    seen = {}

    def fake_fetch(url):
        seen["url"] = url
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"GEOID": "51013", "NAME": "Arlington County"},
                    "geometry": {"type": "Polygon", "coordinates": []},
                }
            ],
        }

    geojson = load_county_geojson("51", fetch_json=fake_fetch)
    labels = county_name_lookup(geojson)

    assert "STATE%3D%2751%27" in seen["url"]
    assert labels["51013"] == "Arlington County"


def test_unknown_state_fips_is_rejected():
    with pytest.raises(ValueError):
        load_county_geojson("99", fetch_json=lambda _: {})
