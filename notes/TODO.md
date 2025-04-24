# Checklist

## Clickable prototype

## /students

- [x] aggregere bikuben hvis ikke fag er valgt
- [x] StudentRow → vis tom bikube for manglende fag, groupId som kolonnetittel
- [x] StudentRow → Expended → Anonymiser navn på mål
- [x] Farge-palett (success)
- [ ] drill into each student
- [x] ui for setting mastery level

## The actual app

- [ ] openapi: kode + typings
- [ ] En test som sjekker at APIet leverer noe og gir 200
- [ ] Fetch noe fra APIet og rendre
- [ ] En unit-test som sjekker noe som helst
- [ ] Auth mot Feide
- [ ] Finne ut av sikkerhet/ACL
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

https://www.django-rest-framework.org/api-guide/parsers/#camelcase-json
https://github.com/Utdanningsdirektoratet/KL06-LK20-public/wiki/Swagger
https://docs.feide.no/reference/apis/groups_api/group_types/pse_teaching.html

This project now have Swagger endpoints with describe the available APIs. I would like to automatically generate frontend code - both request/fetch code and TS typings - using a tool akin to openapi-generator. However, that specific tool requires Java installed locally to run. Which is just ridiculous. Is there another solid tool to achieve the same goals?
