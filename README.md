# Mestring

Prototyping what a keep-track-of-student-mastery app could be
Some [temporary notes](./notes/notes.md).

## Getting started with development

### Problems encountered with Django, MSSQL and macOS

- mssql-django is only compatible with django < 5.1, so you might as well run v4.2.21, open issue here https://github.com/microsoft/mssql-django/issues/418
- mssql-docker is compiled for amd/intel (not arm64). To run on macOS, make sure Docker desktop has Rosetta enabled, open issue https://github.com/microsoft/mssql-docker/issues/802
- Also (for macOSs) you need to install the ODBC drivers which mssql-docker can use:

```
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17 mssql-tools
```

## Importing data

```bash
cd backend
poetry shell
poetry install
python manage.py makemigrations
python manage.py migrate
python import/fetch_feide_groups.py # download all feide groups the application has access to, write all to local groups.json file
python import/import_fetched_groups_to_db.py # import everything in groups.json into the database
python import/fetch_feide_users.py # for groups in the db, download members from feide, write all to local users.json file
python import/import_fetched_users_to_db.py # import everything in users.json into the database
python import/import_from_excel.py # imports any data in the excel file, into the database
```
