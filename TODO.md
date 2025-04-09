# Checklist

## Clickable prototype

## /students

- [x] aggregere bikuben hvis ikke fag er valgt
- [x] StudentRow → vis tom bikube for manglende fag, groupId som kolonnetittel
- [x] StudentRow → Expended → Anonymiser navn på mål
- [x] Farge-palett (success)
- [ ] drill into each student
- [ ] ui for setting mastery level

## The actual app

- [ ] Dockerization
- [ ] Sette opp en database (mariadb?)
- [ ] Sette opp en backend m/gunicorn og django
- [ ] Koble django til databasen
- [ ] Migrasjon som oppretter en tabell og legger inn en rad
- [ ] API: Eksponere innhold fra den ene tabellen via http
- [ ] En test som sjekker at APIet leverer noe og gir 200
- [x] Sette opp en frontend m/svelte
- [x] svelte-routing
- [ ] Fetcher noe fra APIet og rendrer
- [ ] En test som sjekker hva som helst
- [x] Bootstrap
- [ ] Sette opp auth mot Feide
- [ ] Finne ut av sikkerhet/ACL
- [ ] Finne ut av datamodell
- [ ] Konfigurere .env og prosjektet for lokal utvikling og deployment
