<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import { currentUser } from '../stores/data'
  import Groups from './Groups.svelte'
  import { login } from '../stores/auth'
</script>

<section class="py-3">
  {#if $currentUser}
    <Groups />
  {:else}
    <h2 class="mb-4">Hei på deg!</h2>
    <p class="d-flex align-items-center gap-2">Du er visst ikke logget inn.</p>
    <p>
      <pkt-button
        size="small"
        skin="primary"
        type="button"
        variant="label-only"
        onclick={login}
        onkeydown={(e: any) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            login()
          }
        }}
        role="button"
        tabindex="0"
      >
        Logg inn!
      </pkt-button>
    </p>
  {/if}
</section>

<style>
</style>
