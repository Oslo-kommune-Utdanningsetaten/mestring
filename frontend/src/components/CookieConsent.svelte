<script lang="ts">
  import Link from './Link.svelte'
  import { setCookie, getCookie } from '../stores/cookieJar'
  const cookieName = 'cookie_consent'
  let isExpanded = $state(getCookie(cookieName) === null)

  const toggleBanner = () => {
    isExpanded = !isExpanded
  }

  const handleConsent = (choice: 'all' | 'only-necessary') => {
    setCookie(cookieName, choice)
    isExpanded = false
  }
</script>

<div class="consent-container">
  {#if isExpanded}
    <div class="expanded-banner p-4">
      <h4 class="pb-3">Vi bruker informasjonskapsler</h4>
      <pkt-icon name="cookie" class="pkt-icon--large icon-float me-4"></pkt-icon>
      <span>
        For at tjenesten skal fungere, bruker vi informasjonskapsler (cookies). Ved å godta alle,
        hjelper du oss å lage et bedre nettsted. Du kan endre valget ditt når du vil. Uansett hva du
        velger, samler vi ikke inn personlig informasjon.
      </span>
      <div class="buttons-section py-4">
        <button class="custom-button" onclick={() => handleConsent('all')}>Godta alle</button>
        <span class="d-flex align-items-center">
          Muliggjør å logge på, samt sende anonymisert navigasjons-statistikk til Seksjon for
          læringsteknologi
        </span>
        <button class="custom-button" onclick={() => handleConsent('only-necessary')}>
          Kun nødvendige
        </button>
        <span class="d-flex align-items-center">Muliggjør å logge på</span>
      </div>
    </div>
  {:else}
    <Link to="#" onclick={toggleBanner}>Samtykke</Link>
  {/if}
</div>

<style>
  .consent-container {
    display: inline;
    position: relative;
  }

  .expanded-banner {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100vw;
    background: white;
    box-shadow: 0 -10px 10px rgba(0, 0, 0, 0.1);
    z-index: 1000;
  }

  .buttons-section {
    display: grid;
    grid-template-columns: 1fr 4fr;
    grid-column-gap: 2rem;
    grid-row-gap: 1rem;
    margin: auto;
    max-width: 60vw;
    min-width: 300px;
  }

  button {
    font-size: 1rem;
    font-weight: 500;
    padding: 0.2rem 1rem;
  }

  :global(.icon-float) {
    float: left;
    margin-top: 0.5rem;
    margin-right: 1rem;
    margin-bottom: 0.5rem;
  }
</style>
