# Ideer

- Kompetanse bygges stein på stein, nye temaer øker kompetansen selv om man har lav score. Hvordan visualiserer vi kumulativ kompetanse?
  - UI med stein på stein?
  - Achievments?

# Checklist

- [ ] properly responsive navigation bar
- [ ] /students/id
  - [x] personal goals
  - [ ] group goals
- [ ] Teste relasjoner status/goal
- [ ] Smartere Excel-import
- [ ] Finne ut av sikkerhet/ACL
- [ ] Feide
  - [ ] Auth for bruker
  - [x] Importere skoler
  - [x] Importere grupper pr. skole
  - [x] Importere subjects fra UDIR/grep (som matcher teaching-groups)
- [x] deploy to test server
  - [x] basic auth
  - [x] inkludert importere data
- [x] .env example files
- [x] license
- [x] /ping endpoint
  - warning in frontend
- [x] prettier i frontend
- [x] implementer: punkt web components https://punkt.oslo.kommune.no/latest/komponenter/om-komponenter/
- [x] Dataimport fra Excel
  - [x] Observation, Goal
  - [x] User
  - [x] Group
  - [x] Subject
- [x] App funker like bra som prototypen
  - [x] /home (my groups)
  - [x] /students
  - [x] /schools
- [x] /students should show subjects
  - subjects are derived from Goals
- [x] revamp Subject model
- [x] Svelte-kompatibel, datastore-aktig localstorage
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
