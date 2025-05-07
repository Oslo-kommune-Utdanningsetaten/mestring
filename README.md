# Mestring

Prototyping what a keep-track-of-student-mastery app could be

## Getting started with development

### Django, MSSQL and macOS

- mssql-django is only compatible with django < 5.1, so you might as well run v4.2.21, open issue here https://github.com/microsoft/mssql-django/issues/418
- mssql-docker is compiled for amd/intel (not arm64). To run on macOS, make sure Docker desktop has Rosetta enabled, open issue https://github.com/microsoft/mssql-docker/issues/802
- Also (for macOSs) you need to install the ODBC drivers which mssql-docker can use:

```
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17 mssql-tools
```

## Importing data

```
cd backend
python import/fetch_feide_groups.py
python import/import_fetched_groups_to_db.py
```

## Some terms to keep in mind

- Goal

  - observation
  - remark
  - opinion
  - note
  - feedback
  - assessment
  - appraisal

- Mål
  - observasjon
  - bemerkning
  - mening
  - merknad
  - tilbakemelding
  - vurdering
  - taksering
