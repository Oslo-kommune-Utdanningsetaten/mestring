# Programvare med innebygd personvern

Inspirert av [originaldokumentet hos Datatilsynet](https://www.datatilsynet.no/rettigheter-og-plikter/virksomhetenes-plikter/programvareutvikling-med-innebygd-personvern/) og reformatert for praktisk bruk - som en sjekkliste.

1. **Opplæring**  
  - Dørge for at alle som jobber på prosjektet har nødvendig kunnskap og GDPR og personvern, inkludert forståelse av innsynsrett, dataminimering og lagringsbegrensning.
  - De teknisk involverte har god forståelse for sikkerhet på Internett.

2. **Krav**  
  - Kartlegge databehandlingen: Hvilke data, formål, rettslig grunnlag og aktører.  
  - Definere klare sikkerhets- og personvernkrav, inkl. pseudonymisering og dataminimering.
  - Oversikt over databehandleravtaler og hvem som følger opp eksterne leverandører.

3. **Design**  
  - Implementere prinsipper som "minimer og begrens" samt "personvern som standard".  
  - Hvis mulig/der det er aktuelt: Bruke teknikker som kryptering, pseudonymisering og dataseparasjon.
  - Gjennomføre trusselmodellering for å identifisere og redusere angrepsflater.

4. **Koding**  
  - Bruke sikre kodeverktøy og anerkjente biblioteker.
  - Følg med på sikkerthetsoppdteringer av tredjeparts biblioteker, og oppdater disse regelmessig og vedbehov. 
  - Utføre code reviews, gjerne også av eksterne.  
  - Sørge for at data ikke transporteres i klartekst.

5. **Test**  
  - Benytte automatiserte tester (unit og api) som verifiserer at sikkerhetskrav blir fulgt.
  - Gjennomføre både statisk (f.eks. https://pmd.github.io/ eller andre?) og dynamisk testing (automatiserte tester, se over), inkludert sårbarhetsskanning og penetrasjonstesting.
  - Teste at alle brukerrettigheter (innsyn, endring, sletting) fungerer som de skal.

6. **Produksjonssetting**  
  - Når ting går galt er det lurt å vite hvordan det skal håndteres. Etabler en plan for hendelseshåndtering med tydelige kontaktpunkter og responstider.
  - Gjøre en siste sikkerhets- og personvernvurdering før produksjonssetting?

7. **Forvaltning**  
  - Overvåk systemer og loggfør hendelser.  
  - Ha en plan for oppdatering, feilretting og patching av egen programvare og tredjepartskomponenter.
  - Løpende kontroller og forvaltning av tilgangsrettigheter.
