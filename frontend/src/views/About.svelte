<script lang="ts">
  import PersonSVG from '../assets/person.svg.svelte'
  import Link from '../components/Link.svelte'
</script>

<h2 class="my-3">Om tjenesten</h2>
<section class="my-4">
  <ul>
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

<section class="my-3">
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
