Livssyklus for personopplysninger i Mestring

Mestring behandler personopplysninger om elever og lærere ved Oslo-skoler. Opplysningene omfatter fullt navn, Feide-ID, e-postadresse (avledet fra Feide-ID), gruppetilhørighet, rolle (elev/lærer), samt pedagogiske vurderingsdata i form av observasjoner, måloppnåelse og framovermeldinger knyttet til den enkelte elev.

Personopplysningene innhentes fra Feide gjennom en daglig, automatisert importjobb per skole. Importen skjer i fem steg via OAuth2-autentisert API-tilgang:

1. Hente gruppedata
2. Hente medlemskap med personopplysninger
3. Lagre grupper i databasen
4. Lagre brukere og deres gruppetilknytninger
5. Opprydding av data som ikke lenger finnes i Feide.

Mellom steg 2 og 4 mellomlagres personopplysninger (navn, Feide-ID, e-post, rolle) som JSON-filer på applikasjonsserverens filsystem. Disse filene slettes når de ikke lenger trengs.

Vurderingsdata (observasjoner, mål og status) opprettes manuelt av lærere i applikasjonen og knyttes til navngitte elever. Dette er de mest sensitive personopplysningene i løsningen, da de inneholder fritekst-vurderinger av elevers faglige mestring.

Vedlikehold av data skjer gjennom den daglige importjobben, som oppdaterer et tidsstempel (maintained_at) på alle entiteter den berører. Entiteter som ikke bekreftes av Feide ved import (f.eks. elever som har byttet skole eller grupper som er avsluttet) merkes med et slettingstidsstempel (deleted_at, myk sletting). Merkede data er umiddelbart usynlige for brukerne. I tillegg har grupper gyldighetsperioder (valid_from/valid_to) fra Feide som automatisk begrenser synligheten av grupper og tilhørende medlemskap til det inneværende skoleåret.

Permanent sletting (hard delete) utføres av en oppryddingsjobb som kjører etter hver import. Alle mykt slettede entiteter (brukere, grupper, observasjoner, mål og statuser) slettes irreversibelt fra databasen 90 dager etter at de har blitt "mykt" slettet. Gruppetilknytninger (UserGroup) har en kortere oppbevaringsperiode på 1 time, ettersom tilganger bør fjernes raskt. Kaskadesletting: Når en bruker slettes permanent, fjernes også alle tilknyttede observasjoner, mål, statuser og gruppetilknytninger via databasens kaskaderegler.

Dersom en tidligere slettet bruker eller gruppe gjenoppstår (gjennom en senere import fra Feide) før den har blitt "hardt" slettet, fjernes slettemerket og tilhørende vurderingsdata gjenopprettes.

Skoleadministratorer og inspektører tildeles manuelt i systemet og følger ikke den automatiserte livssyklusen. Det finnes pr. tiden ingen automatisk nedgradering av disse rollene ved skoleårsskifte, men kan implementeres ved behov.
