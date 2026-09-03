# Security Policy

## Scope

This is a research prototype. Security reports are welcome for repository, dependency,
workflow, or deployment issues.

## Reporting

Please use GitHub's private security-reporting mechanism when available. Do not include
secrets, credentials, private financial records, or personally identifiable information
in a public issue.

## Secrets

The default project requires no API key.

If future integrations require credentials:

- store them in environment variables or a secret manager;
- never hard-code them in source;
- never commit `.env` files; and
- rotate any credential that is accidentally exposed.

## Data safety

Do not use this repository to store real applicant records unless an appropriate data
governance, privacy, retention, and access-control process has been established.
