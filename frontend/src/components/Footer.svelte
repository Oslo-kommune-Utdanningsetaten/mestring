<script lang="ts">
  import Link from './Link.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import { version } from '../../package.json'
</script>

<footer class="navbar container-md p-3" data-mode="auto">
  <div class="d-flex flex-column flex-md-row align-items-start w-100 gap-3">
    <div>
      <div>
        <Link to="https://www.oslo.kommune.no/etater-foretak-og-ombud/utdanningsetaten/">
          Oslo kommune, Utdanningsetaten
        </Link>
      </div>
      <div class="mt-1 version">
        mestring v{version}
      </div>
    </div>

    <div class="ms-md-auto">
      <ul class="footer-links">
        <li>
          <Link to="/about">Om tjenesten</Link>
        </li>
        <li><Link to="/about">Personvern</Link></li>
        <li>
          <Link
            to="https://uustatus.no/nb/erklaringer/publisert/cd426ab2-6214-4fb8-bec4-7d637b139e0a"
          >
            Tilgjengelighet
          </Link>
        </li>
      </ul>
      <div class="mt-1">
        <Link
          to="https://github.com/Oslo-kommune-Utdanningsetaten/mestring"
          title="Mestring på GitHub"
        >
          <pkt-icon name="github" class="pkt-icon--medium"></pkt-icon>
        </Link>
        <a
          href="mailto:TBA"
          onclick={event => {
            event.preventDefault()
            alert('Kommer snart!')
          }}
          title="Kontakt via e-post"
        >
          <pkt-icon name="email" class="pkt-icon--medium"></pkt-icon>
        </a>
      </div>
    </div>
  </div>
</footer>

<style>
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    li {
      display: inline;
      margin-right: 1rem;
    }
  }

  .version {
    font-family: 'Courier New', Courier, monospace;
  }
</style>
