<script lang="ts">
  import Link from '../components/Link.svelte'
  import { fetchMetadata } from '../generated/sdk.gen'
  import { dataStore } from '../stores/data'
  import { GROUP_TYPE_BASIS, GROUP_TYPE_TEACHING, USER_ROLES } from '../utils/constants'
  import { hasUserAccessToPath } from '../stores/access'

  let metadata = $state<Record<string, any>>({})
  const { currentSchool, currentUser } = $derived($dataStore)

  const fetchServiceMetadata = async () => {
    try {
      const options = currentSchool ? { query: { orgNumber: currentSchool.orgNumber } } : {}
      const metadataResult = await fetchMetadata(options)
      metadata = metadataResult.data || {}
    } catch (error) {
      console.error('Error fetching service metadata:', error)
    }
  }

  const getRoleCount = (role: string, teacherType?: string) => {
    if (!metadata.roleCounts) {
      return 0
    }
    return teacherType ? metadata.roleCounts[role][teacherType] : metadata.roleCounts[role]
  }

  $effect(() => {
    if (currentUser) fetchServiceMetadata()
  })
</script>

{#snippet rolesCount(role: string, teacherType?: string)}
  {@const linkTo = `/users?role=${role}${teacherType ? `&teacherType=${teacherType}` : ''}`}
  {@const count = getRoleCount(role, teacherType)}
  {@const schoolName =
    currentSchool && role !== USER_ROLES.SUPERADMIN ? ` ved ${currentSchool.displayName}` : ''}
  {#if currentUser && $hasUserAccessToPath('/users')}
    <Link to={linkTo}>
      {count + ` ${count == 1 ? 'person' : 'personer'} har denne rollen${schoolName}`}.
    </Link>
  {:else if currentUser}
    {count + ` ${count == 1 ? 'person' : 'personer'} har denne rollen${schoolName}`}.
  {/if}
{/snippet}

<!-- About the app -->
<section class="mt-3 mb-5" id="about">
  <h2>Hva er mestring.osloskolen.no?</h2>
  <p class="mb-4">
    Webapplikasjonen er utviklet av UDA for å gi lærere og skoleledelse bedre oversikt over elevenes
    faglige utvikling. Løsningen gjør underveisvurdering i en travel hverdag enklere ved å samle mål
    og løpende observasjoner på ett sted. Samtidig får ledelsen oversikt over hvilke elever som
    trenger ekstra innsats.
  </p>

  <h3>Hovedfunksjoner</h3>
  <ul>
    <li>
      <span class="fw-bold">Enkelt:</span>
      Det krever få klikk for læreren å registrere løpende observasjoner.
    </li>
    <li>
      <span class="fw-bold">Målsetting:</span>
      Læreren kan sette individuelle mål for hver enkelt elev, eller felles mål for en hel gruppe (for
      eksempel faglige temaer eller kompetansemål).
    </li>
    <li>
      <span class="fw-bold">Metodefrihet:</span>
      Løsningen ble opprinnelig bygget rundt «Mestringstrappa» for Stig skole, men støtter også kvalitative
      kommentarer, klassisk karakterskala og metodikker som «two stars and a wish».
    </li>
  </ul>

  <h3>Fordeler med løsningen</h3>
  <ul>
    <li>
      <span class="fw-bold">For læreren:</span>
      Frigjør tid ved å erstatte parallell skyggeføring i Excel-ark, Word-filer eller OneNote. Gir oversikt
      over elevens prosess og faglige progresjon.
    </li>
    <li>
      <span class="fw-bold">For ledelsen:</span>
      Gir oversikt over hvilke elever som kan trenge ekstra ressurser eller tilrettelegging.
    </li>
    <li>
      <span class="fw-bold">For skolen:</span>
      Bruk av et felles verktøy bidrar til en likere, mer enhetlig og rettferdig vurderingspraksis.
    </li>
    <li>
      <span class="fw-bold">Videre utvikling:</span>
      Løsningen er ikke «hyllevare», men utviklet av og for Osloskolen. Det betyr at feil rettes fort,
      og vi står fritt til å implementere funksjonalitet som skolene trenger.
    </li>
  </ul>
</section>

<!-- General technicalities -->
<section class="mt-3 mb-5">
  <h2>Teknisk om tjenesten</h2>

  <ul>
    <li>
      Utviklet av Seksjon for Læringsteknologi i
      <Link to="https://www.oslo.kommune.no/etater-foretak-og-ombud/utdanningsetaten/">
        Utdanningsetaten
      </Link>
      i tett samarbeid med
      <Link to="https://stig.osloskolen.no/">Stig skole</Link>.
    </li>
    <li>
      Kildekoden er åpen og tilgjengelig på
      <Link to="https://github.com/Oslo-kommune-Utdanningsetaten/mestring/">GitHub</Link>, og her er
      <Link to="https://github.com/Oslo-kommune-Utdanningsetaten/mestring/issues">oppgavene</Link>
      vi jobber med.
    </li>
  </ul>

  <h3 id="guidelines">Retningslinjer for bruk</h3>
  <ul>
    <li>Minimér informasjon som kan knyttes til personer.</li>
    <li>Der det er mulig, bruk nøytrale, ikke-sensitive formuleringer om personer.</li>
    <li>Husk å låse PCen, slik at andre ikke kan få tilgang til informasjon via din bruker.</li>
    <li>Ikke ta utskrifter - papir har en tendens til å bli liggende der andre har tilgang.</li>
  </ul>

  <!-- Access info -->
  <h3 id="access">Hvem har tilgang til hva?</h3>
  <ul>
    <li>
      <span class="fw-bold">Lærer i undervisningsgruppe</span>
      kan opprette mål og observasjoner for elevene gruppa, i faget som undervises.
      {@render rolesCount(USER_ROLES.TEACHER, GROUP_TYPE_TEACHING)}
    </li>
    <li>
      <span class="fw-bold">Lærer i basisgruppe</span>
      kan se mål og observasjoner for sine elever, i alle fag. Kan opprette individuelle mål (og observasjoner
      på disse) for sine elever i alle fag.
      {@render rolesCount(USER_ROLES.TEACHER, GROUP_TYPE_BASIS)}
    </li>
    <li>
      <span class="fw-bold">Skoleinspektør</span>
      kan se mål og observasjoner for alle elever ved {currentSchool
        ? currentSchool.displayName
        : 'sin skole'}.
      {@render rolesCount(USER_ROLES.INSPECTOR)}
    </li>
    <li>
      <span class="fw-bold">Skoleadmin</span>
      kan se og redigere mål og observasjoner for alle elever ved {currentSchool
        ? currentSchool.displayName
        : 'sin skole'}.
      {@render rolesCount(USER_ROLES.ADMIN)}
    </li>
    <li>
      <span class="fw-bold">Superadmin</span>
      kan se og redigere mål og observasjoner for alle elever ved alle skoler. Kan også endre globale
      innstillinger for skolene.
      {@render rolesCount(USER_ROLES.SUPERADMIN)}
    </li>
  </ul>

  <!-- Data retention info -->
  <h3>Hvor lenge lagres data?</h3>
  {#if metadata.deleteRules}
    <ul>
      {#each Object.values(metadata.deleteRules) as deleteRule}
        <li>
          {deleteRule}
        </li>
      {/each}
    </ul>
  {:else}
    <p>Logg på for å se oppdatert informasjon om datalagring.</p>
  {/if}

  <!-- About the icons -->
  <h3>Hva betyr ikonene?</h3>
  <p>
    Ikonene i mestring er hentet fra
    <Link to="https://punkt.oslo.kommune.no/latest/ikoner/">Punkt</Link>
    og har følgende betydning:
  </p>
  <div class="icon-grid mt-4">
    <div class="icon">
      <span class="svg-container" title="Person">
        <pkt-icon name="person"></pkt-icon>
      </span>
      <span class="icon-label">Person</span>
    </div>

    <div class="icon">
      <span class="svg-container" title="Gruppe">
        <pkt-icon name="group"></pkt-icon>
      </span>
      <span class="icon-label">Gruppe</span>
    </div>

    <div class="icon">
      <span class="svg-container" title="Elev">
        <pkt-icon name="education"></pkt-icon>
      </span>
      <span class="icon-label">Elev</span>
    </div>

    <div class="icon">
      <span class="svg-container" title="Lærer">
        <pkt-icon name="lecture"></pkt-icon>
      </span>
      <span class="icon-label">Lærer</span>
    </div>

    <div class="icon">
      <span class="svg-container" title="Mål">
        <pkt-icon name="goal"></pkt-icon>
      </span>
      <span class="icon-label">Mål</span>
    </div>

    <div class="icon">
      <span class="svg-container" title="Observasjon">
        <pkt-icon name="bullseye"></pkt-icon>
      </span>
      <span class="icon-label">Observasjon</span>
    </div>

    <div class="icon">
      <span class="svg-container" title="Status">
        <pkt-icon name="achievement"></pkt-icon>
      </span>
      <span class="icon-label">Status</span>
    </div>

    <div class="icon">
      <span class="svg-container" title="Slett">
        <pkt-icon name="trash-can"></pkt-icon>
      </span>
      <span class="icon-label">Slett</span>
    </div>

    <div class="icon">
      <span class="svg-container" title="Rediger">
        <pkt-icon name="edit"></pkt-icon>
      </span>
      <span class="icon-label">Rediger</span>
    </div>
  </div>
</section>

<style>
  li {
    margin-bottom: 0.8rem;
  }

  h2,
  h3 {
    margin-top: 1rem;
    margin-bottom: 1rem;
  }

  ul {
    margin-top: 1rem;
    margin-bottom: 2rem;
  }

  .icon-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 3rem;
  }

  .icon {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
  }

  .svg-container {
    display: inline-block;
    width: 100px;
  }

  .svg-container :global(svg) {
    width: 100%;
    height: 100%;
  }

  .icon-label {
    text-align: center;
  }
</style>
