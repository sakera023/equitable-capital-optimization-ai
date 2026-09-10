# Certified CDFI Public-Data Context

## Source

The project integrates the official **List of Currently Certified CDFIs** published by the
Community Development Financial Institutions Fund, U.S. Department of the Treasury:

https://www.cdfifund.gov/programs-training/certification/cdfi

The software discovers the current workbook link from the official source page and keeps a
fallback official resource URL for resilience.

## Validation safeguards

CDFI workbooks can include summary and institution-level worksheets. The loader therefore:

1. identifies state-bearing worksheets;
2. requires an organization-name column;
3. prefers the candidate with the greatest number of recognized institution-state rows;
4. rejects a candidate with fewer than 100 recognized institution rows.

This prevents a small state-summary sheet from being mistaken for the underlying Certified
CDFI organization roster.

## State summary

The research helper reports:

- unique Certified CDFI organizations by state; and
- number of institution types when that field is available.

## Interpretation boundary

An organization's listed state is **not** equivalent to lending volume, branch presence,
target-market coverage, service-area access, approval rates, or actual capital received by
small businesses in that state. The CDFI layer is a descriptive institutional-geography
context measure and should be interpreted together with the CDFI Fund's own definitions and
program documentation.
