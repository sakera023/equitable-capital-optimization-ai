# U.S. Census Annual Business Survey Integration

## Source

The project supports the official U.S. Census Bureau **Annual Business Survey (ABS) 2022
Company Summary** API:

- Dataset documentation: https://www.census.gov/data/developers/data-sets/abs.html
- API endpoint: https://api.census.gov/data/2022/abscs
- Official examples: https://api.census.gov/data/2022/abscs/examples.html
- Variables: https://api.census.gov/data/2022/abscs/variables.html

The integrated measures include employer firms (`FIRMPDEMP`), employees (`EMP`), receipts
(`RCPPDEMP`), and annual payroll (`PAYANN`) together with Census geography and demographic
classification fields.

## API key and security

Census currently requires an API key for data queries. The software accepts the key only
at runtime through either:

- the `api_key=` function argument; or
- the `CENSUS_API_KEY` environment variable.

No API key belongs in source code, notebooks, screenshots, commits, issues, or example
configuration.

## Geographic support

The module provides:

- national state queries; and
- county queries scoped to a selected two-digit Census state FIPS code.

County responses receive a five-digit `geoid` when both state and county codes are
available.

## Avoiding demographic double counting

ABS company-summary responses can contain multiple rows for demographic categories. The
project therefore does **not** sum those rows into a state or county total. The helper
`total_population_rows()` accepts rows only when the returned label fields explicitly
identify total categories; otherwise it returns no aggregate rather than inferring Census
codes.

This conservative rule protects research users from treating overlapping demographic
categories as additive populations.

## Research boundary

ABS is an authoritative aggregate public-data layer. It is kept separate from the
synthetic applicant-level predictive model and is not presented as external validation of
individual funding probabilities. It is intended for contextual entrepreneurship and
business-ecosystem research.
