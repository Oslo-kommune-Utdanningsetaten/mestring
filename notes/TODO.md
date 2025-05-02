# Checklist

- [x] Urls, view, serializers for hele databasen
- [x] Teste relasjoner user/group
- [ ] Teste relasjoner status/goal
- [ ] Dataimport fra Excel

I need import data from an Excel file and write rows in the database. This requires several steps:

- The models.py file dictates the target shape of the data should have
- Figure out how to structure data in the excel file (available either as a file or on a URL, read access)
- Apply some samples from the schoolData_v2.js file to the Excel file, establishing a pattern how users will be entering data
- A script which reads the excel file, builds an internal data structure and writes rows to the database, in the appropriate tables
- The script should be able to run repeatedly, without creating duplicates
- I have a preference for node.js (above python) so this should be a JS file which resides in the /scripts folder

- [ ] App funker like bra som prototypen
- [ ] En unit-test som sjekker noe som helst
- [ ] Auth mot Feide
- [ ] Finne ut av sikkerhet/ACL
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

## linker

https://github.com/Utdanningsdirektoratet/KL06-LK20-public/wiki/Swagger
https://docs.feide.no/reference/apis/groups_api/group_types/pse_teaching.html
