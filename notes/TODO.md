# Checklist

- [ ] App funker like bra som prototypen
  - [ ] /home (my groups)
  - [ ] /students
  - [x] /schools
- [ ] prettier i frontend
- [ ] Finne ut av sikkerhet/ACL
- [ ] Svelte-kompatibel, datastore-aktig localstorage
- [ ] Teste relasjoner status/goal
- [ ] Vanntett import med god logging
- [ ] Feide
  - [ ] Auth for bruker
  - [x] Importere skoler
  - [x] Importere grupper pr. skole
  - [x] Importere subjects fra UDIR/grep (som matcher teaching-groups)
- [x] Dataimport fra Excel
  - [x] Observation, Goal
- [x] En unit-test som sjekker noe som helst
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

# Pattern for feide_id:

feide_id pattern for School:
fc:org:kakrafoon.kommune.no:unit:NO987654321

feide_id pattern for teaching group (the "u" is for "undervisningsgruppe"):
fc:org:kakrafoon.kommune.no:<u>:NO987654321:<3a-matte>:2000-07-01:2100-06-30"

feide_id for basis group (the "b" is for "basissgruppe"):
fc:org:kakrafoon.kommune.no:<b>:NO987654321:<3a>:2000-07-01:2100-06-30"

Feide_id for User:
feide:<username>@feide.osloskolen.no

# Links

https://www.udir.no/om-udir/data/kl06-grep/
https://github.com/Utdanningsdirektoratet/KL06-LK20-public/wiki/Swagger
https://docs.feide.no/reference/apis/groups_api/group_types/pse_teaching.html
