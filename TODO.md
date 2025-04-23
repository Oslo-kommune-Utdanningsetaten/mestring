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

- [ ] Skissere en datamodell
- [ ] Modellfiler
- [ ] Sette opp en database, mariadb
- [ ] Koble django til databasen
- [ ] Generere og kjøre migrasjoner
- [ ] API: Eksponere innhold fra den ene tabellen via http
- [ ] En test som sjekker at APIet leverer noe og gir 200
- [ ] Fetch noe fra APIet og rendrere
- [ ] En unit-test som sjekker noe som helst
- [ ] Auth mot Feide
- [ ] Konfigurere .env og prosjektet for lokal utvikling og deployment
- [ ] Finne ut av sikkerhet/ACL
- [ ] Dockerization m/gunicorn
- [x] Sette opp en frontend m/svelte
- [x] svelte-routing
- [x] Bootstrap

## linker

https://www.django-rest-framework.org/api-guide/parsers/#camelcase-json
https://github.com/Utdanningsdirektoratet/KL06-LK20-public/wiki/Swagger
https://docs.feide.no/reference/apis/groups_api/group_types/pse_teaching.html
