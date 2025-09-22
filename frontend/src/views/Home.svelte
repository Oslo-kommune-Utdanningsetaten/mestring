<script lang="ts">
  // Replaced direct pkt-button usage with ButtonMini wrapper
  import ButtonMini from '../components/ButtonMini.svelte'
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
      <ButtonMini
        options={{
          title: 'Logg inn!',
          iconName: 'login',
          skin: 'primary',
          variant: 'label-only',
          classes: '',
          onClick: () => login(),
        }}
      >
        Logg inn!
      </ButtonMini>
    </p>
  {/if}
</section>

<style>
</style>
