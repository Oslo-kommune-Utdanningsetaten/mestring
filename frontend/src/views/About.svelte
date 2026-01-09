<script lang="ts">
  import PersonSVG from '../assets/person.svg.svelte'
</script>

<h2 class="my-3">Om tjenesten</h2>
<section class="my-4">
  <ul>
    <li>
      mestring.osloskolen.no er en prototype på hvordan det går an holde oversikt over elevers
      mestring fagene
    </li>
    <li>
      Utviklet av Seksjon for Læringsteknologi i <a
        href="https://www.oslo.kommune.no/etater-foretak-og-ombud/utdanningsetaten/"
        target="_blank"
      >
        Utdanningsetaten
      </a>
      i tett samarbeid med
      <a href="https://haukasen.osloskolen.no/" target="_blank">Haukåsen skole</a>
    </li>
    <li>
      Kildekoden er åpen og tilgjengelig på <a
        href="https://github.com/Oslo-kommune-Utdanningsetaten/mestring/"
        target="_blank"
      >
        GitHub
      </a>
    </li>
    <li>
      Her finner du <a
        href="https://github.com/Oslo-kommune-Utdanningsetaten/mestring/issues"
        target="_blank"
      >
        oppgavene
      </a>
      vi jobber med
    </li>
  </ul>
</section>

<section class="my-3">
  <h3>Hva betyr ikonene?</h3>
  <p class="my-3">
    Ikonene i mestring er hentet fra
    <a href="https://punkt.oslo.kommune.no/latest/ikoner/" target="_blank">Punkt</a>
    og har følgende betydning:
  </p>
  <div class="icon-grid">
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
        <pkt-icon name="graph"></pkt-icon>
      </span>
      <span class="icon-label">Status</span>
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
