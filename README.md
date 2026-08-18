# Mestring

## Hva er mestring.osloskolen.no?

- En tjeneste som gjør det enkelt for lærere å holde oversikt over hvordan det står til med elevenes mestring i de ulike fagene.
- Gi skolens ledelse en måte å holde oversikt over hvordan det står til på skolen generelt + fange opp elever som sliter.
- Det er foreløpig bare primitiv støtte for at elever kan bruke tjenesten, og ingen støtte for foreldretilgang.
- Klienten (det som brukerne forholder seg til) er et webgrensesnitt og funker på alle moderne nettlesere.
- Pålogging + datasynkronisering (brukere, grupper og tilganger) skjer via Feide.
- Programvaren er gratis å bruke, men du må kunne installere og host'e hele løsningen selv. Når dette er satt opp, kan tjenesten brukes for alle skolene i kommunen.

## Dev notes

- Svelte frontend
- Python w/django backend
- PostgreSQL database
- Check out the [data model](./notes/mestring-diagram.drawio.png)

- Some [old notes](./notes/old-notes.md)

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
```

### Problems encountered with Django, MSSQL and macOS

- mssql-django is only compatible with django < 5.1, so you might as well run v4.2.21, open issue here https://github.com/microsoft/mssql-django/issues/418
- mssql-docker is compiled for amd/intel (not arm64). To run on macOS, make sure Docker desktop has Rosetta enabled, open issue https://github.com/microsoft/mssql-docker/issues/802
- Also (for macOSs) you need to install the ODBC drivers which mssql-docker can use:

```
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17 mssql-tools
```
