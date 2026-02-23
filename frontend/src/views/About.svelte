<script lang="ts">
  import { fetchMetadata } from '../generated/sdk.gen'
  import { dataStore } from '../stores/data'
  import Link from '../components/Link.svelte'
  let metadata = $state<Record<string, any>>({})

  const fetchServiceMetadata = async () => {
    try {
      const options = $dataStore.currentSchool
        ? { query: { orgNumber: $dataStore.currentSchool.orgNumber } }
        : {}
      const metadataResult = await fetchMetadata(options)
      metadata = metadataResult.data || {}
    } catch (error) {
      console.error('Error fetching service metadata:', error)
    }
  }

  $effect(() => {
    const currentSchool = $dataStore.currentSchool
    fetchServiceMetadata()
  })
</script>

{#snippet rolesCount(role: string)}
  {#if Object.hasOwn(metadata, 'roleCounts') && Object.hasOwn(metadata.roleCounts, role)}
    <span>
      {metadata.roleCounts[role] +
        ` ${metadata.roleCounts[role] == 1 ? 'person' : 'personer'} har denne rollen.`}
    </span>
  {/if}
{/snippet}

<!-- About the app -->
<section class="mt-3 mb-5">
  <h2 class="my-3">Om tjenesten</h2>
  <ul class="my-3">
    <li>
      mestring.osloskolen.no er en prototype på hvordan det går an holde oversikt over elevers
      mestring fagene
    </li>
    <li>
      Utviklet av Seksjon for Læringsteknologi i
      <Link to="https://www.oslo.kommune.no/etater-foretak-og-ombud/utdanningsetaten/">
        Utdanningsetaten
      </Link>
      i tett samarbeid med
      <Link to="https://haukasen.osloskolen.no/">Haukåsen skole</Link>
    </li>
    <li>
      Kildekoden er åpen og tilgjengelig på
      <Link to="https://github.com/Oslo-kommune-Utdanningsetaten/mestring/">GitHub</Link>
    </li>
    <li>
      Her finner du
      <Link to="https://github.com/Oslo-kommune-Utdanningsetaten/mestring/issues">oppgavene</Link>
      vi jobber med
    </li>
  </ul>
</section>

<!-- Access info -->
<section class="my-5">
  <h3>Hvem har tilgang til hva?</h3>
  <ul class="my-3">
    <li>
      <span class="fw-bold">Lærer i undervisningsgruppe</span>
      kan opprette mål og observasjoner for elevene gruppa, i faget som undervises. {@render rolesCount(
        'teacherTeaching'
      )}
    </li>
    <li>
      <span class="fw-bold">Lærer i basisgruppe</span>
      kan se mål og observasjoner for sine elever, i alle fag. Kan opprette individuelle mål (og observasjonerpå
      disse) for sine elever i alle fag. {@render rolesCount('teacherBasis')}
    </li>
    <li>
      <span class="fw-bold">Skoleinspektør</span>
      kan se mål og observasjoner for alle elever ved sin skole. {@render rolesCount('inspector')}
    </li>
    <li>
      <span class="fw-bold">Skoleadmin</span>
      kan se og redigere mål og observasjoner for alle elever ved sin skole. {@render rolesCount(
        'admin'
      )}
    </li>
    <li>
      <span class="fw-bold">Superadmin</span>
      kan se og redigere mål og observasjoner for alle elever ved alle skoler. Kan også endre globale
      innstillinger for skolene. {@render rolesCount('superadmin')}
    </li>
  </ul>
</section>

<!-- Data retention info -->
<section class="my-5">
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

<section class="my-5">
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
