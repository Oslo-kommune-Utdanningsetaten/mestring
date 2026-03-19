<script lang="ts">
  import Link from '../components/Link.svelte'
  import { fetchMetadata } from '../generated/sdk.gen'
  import { dataStore } from '../stores/data'
  import { GROUP_TYPE_BASIS, GROUP_TYPE_TEACHING, USER_ROLES } from '../utils/constants'
  import { hasUserAccessToPath } from '../stores/access'

  let metadata = $state<Record<string, any>>({})
  const currentSchool = $derived($dataStore.currentSchool)
  const currentUser = $derived($dataStore.currentUser)

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
  {#if currentUser && $hasUserAccessToPath('/users')}
    <Link to={linkTo}>
      {count + ` ${count == 1 ? 'person' : 'personer'} har denne rollen`}.
    </Link>
  {:else if currentUser}
    {count + ` ${count == 1 ? 'person' : 'personer'} har denne rollen`}.
  {/if}
{/snippet}

<!-- About the app -->
<section class="mt-3 mb-5" id="about">
  <h2 class="my-3">Om tjenesten</h2>
  <ul class="my-3">
    <li>
      Denne tjenesten (kjent som "Mestring") er en prototype på hvordan det går an holde oversikt
      over elevers mestring fagene.
    </li>
    <li>
      Utviklet av Seksjon for Læringsteknologi i
      <Link to="https://www.oslo.kommune.no/etater-foretak-og-ombud/utdanningsetaten/">
        Utdanningsetaten
      </Link>
      i tett samarbeid med
      <Link to="https://haukasen.osloskolen.no/">Haukåsen skole</Link>.
    </li>
    <li>
      Kildekoden er åpen og tilgjengelig på
      <Link to="https://github.com/Oslo-kommune-Utdanningsetaten/mestring/">GitHub</Link>.
    </li>
    <li>
      Her finner du
      <Link to="https://github.com/Oslo-kommune-Utdanningsetaten/mestring/issues">oppgavene</Link>
      vi jobber med.
    </li>
  </ul>
</section>

<!-- General guidelines -->
<section class="mt-3 mb-5" id="guidelines">
  <h2 class="my-3">Retningslinjer for bruk</h2>
  <ul class="my-3">
    <li>Minimér informasjon som kan knyttes til personer.</li>
    <li>Der det er mulig, bruk nøytrale, ikke-sensitive formuleringer om personer.</li>
    <li>Husk å låse PCen, slik at andre ikke kan få tilgang til informasjon via din bruker.</li>
    <li>Ikke ta utskrifter - papir har en tendens til å bli liggende der andre har tilgang.</li>
  </ul>
</section>

<!-- Access info -->
<section class="my-5" id="access">
  <h3>Hvem har tilgang til hva?</h3>
  <ul class="my-3">
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
      kan se mål og observasjoner for alle elever ved sin skole.
      {@render rolesCount(USER_ROLES.INSPECTOR)}
    </li>
    <li>
      <span class="fw-bold">Skoleadmin</span>
      kan se og redigere mål og observasjoner for alle elever ved sin skole.
      {@render rolesCount(USER_ROLES.ADMIN)}
    </li>
    <li>
      <span class="fw-bold">Superadmin</span>
      kan se og redigere mål og observasjoner for alle elever ved alle skoler. Kan også endre globale
      innstillinger for skolene.
      {@render rolesCount(USER_ROLES.SUPERADMIN)}
    </li>
  </ul>
</section>

<!-- Data retention info -->
<section class="my-5" id="storage">
  <h3>Hvor lenge lagres data?</h3>
  {#if metadata.deleteRules}
    <ul class="my-3">
      {#each Object.values(metadata.deleteRules) as deleteRule}
        <li>
          {deleteRule}
        </li>
      {/each}
    </ul>
  {:else}
    asdf
  {/if}
</section>

<section class="my-5" id="icons">
  <h3>Hva betyr ikonene?</h3>
  <p class="my-3">
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
      <span class="svg-container" title="Status">
        <pkt-icon name="trash-can"></pkt-icon>
      </span>
      <span class="icon-label">Slett</span>
    </div>

    <div class="icon">
      <span class="svg-container" title="Status">
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
