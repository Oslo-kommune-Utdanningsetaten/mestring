# Checklist

- [ ] Teste relasjoner status/goal
- [ ] Dataimport fra Excel
- [ ] prettier i frontend
- [ ] App funker like bra som prototypen
- [ ] Feide
  - [ ] Auth
  - [ ] Skoler
  - [ ] Grupper pr. skole
- [ ] Finne ut av sikkerhet/ACL
- [ ] En unit-test som sjekker noe som helst
- [x] Urls, view, serializers for hele databasen
- [x] Teste relasjoner user/group
- [x] En test som sjekker at APIet leverer noe og gir 200
- [x] openapi: kode + typings
- [x] Fetch noe fra APIet og rendre
- [x] API with camelCase
- [x] Skissere en datamodell
- [x] models.py
- [x] Sette opp en database, mariadb
- [x] Koble django til databasen
- [x] Generere og kjøre migrasjoner
- [x] API: Eksponere innhold fra den ene tabellen via http
- [x] Konfigurere .env og prosjektet for lokal utvikling og deployment
- [x] Dockerization m/gunicorn
- [x] Sette opp en frontend m/svelte
- [x] svelte-routing
- [x] Bootstrap

# Scratchpad

I need to read data from an Excel file and write rows in the database. This requires several steps:

- The models.py file dictates the target shape of the data should have
- Figure out how to structure data in the excel file (available either as a file or on a URL, read access)
- Apply some samples from the schoolData_v2.js file to the Excel file, establishing a pattern how users will be entering data
- A script which reads the excel file, builds an internal data structure and writes rows to the database, in the appropriate tables
- The script should be able to run repeatedly, without creating duplicates
- This should be a python script, and should rely on the ORM supplied by Django on the backend. I'm thinking ./backend/scripts/import_from_excel.py is a good place to put it
- The script should be able to run from the command line

Here's the pattern for feide_id:

feide_id pattern for School:
fc:org:kakrafoon.kommune.no:unit:NO987654321

feide_id pattern for teaching group (the "u" is for "undervisningsgruppe"):
fc:org:kakrafoon.kommune.no:<u>:NO987654321:<3a-matte>:2000-07-01:2100-06-30"

feide_id for basis group (the "b" is for "basissgruppe"):
fc:org:kakrafoon.kommune.no:<b>:NO987654321:<3a>:2000-07-01:2100-06-30"

Feide_id for User:
feide:<username>@feide.osloskolen.no

# Links

https://github.com/Utdanningsdirektoratet/KL06-LK20-public/wiki/Swagger
https://docs.feide.no/reference/apis/groups_api/group_types/pse_teaching.html
