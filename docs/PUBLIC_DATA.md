# Public U.S. Data Layer

The application includes a separate public-data browser for authoritative U.S.
small-business statistics. This layer is intentionally separated from the synthetic
applicant-level prediction model.

## Current sources

### SBA State Small Business Statistics 2025

Publisher: U.S. Small Business Administration, Office of Advocacy.

Landing page:
https://data.sba.gov/dataset/state-small-business-statistics-2025

The dataset contains state-level statistics derived from the SBA's 2025 Small Business
Profiles, including measures related to the number of small businesses, employment,
job creation, and business ownership.

### SBA Metropolitan Area Small Business Statistics 2025

Publisher: U.S. Small Business Administration, Office of Advocacy.

Landing page:
https://data.sba.gov/dataset/metropolitan-area-small-business-statistics-2025

The dataset provides metropolitan-area small-business indicators for geographic
comparison and contextual analysis.

## Data-access design

The package queries the SBA CKAN open-data catalog at runtime to discover the current
official Excel resource URL. It then downloads the workbook and exposes its sheets in
the Streamlit dashboard.

This design avoids storing a stale copy of the government workbook in the repository.

## Research boundary

The public aggregate data are displayed for contextual and geographic research.
They are **not** used to train the synthetic capital-readiness classifier and should
not be interpreted as validation of applicant-level predictions.

Future work can add additional authoritative sources such as Census business statistics,
CDFI Fund data, and carefully documented geographic joins.
