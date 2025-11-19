<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import { currentUser } from '../stores/data'
  import { login } from '../stores/auth'
  import Groups from './Groups.svelte'
  import ButtonMini from '../components/ButtonMini.svelte'

  const router = useTinyRouter()
  let errorFromUrl = $state<string | undefined>(undefined)

  $effect(() => {
    errorFromUrl = router.getQueryParam('error')
  })
</script>

{#if $currentUser}
  <Groups />
{:else}
  <h2 class="mb-4">Hei på deg!</h2>
  {#if errorFromUrl === 'login_failed'}
    <p>Humf, login mislyktes</p>
  {:else}
    <p>Du er visst ikke logget inn.</p>
    <p>{errorFromUrl}</p>
  {/if}
  <div>
    <ButtonMini
      options={{
        title: 'Logg inn!',
        iconName: 'login',
        skin: 'primary',
        variant: 'label-only',
        onClick: () => login(),
      }}
    >
      Logg inn!
    </ButtonMini>
  </div>
{/if}

<style>
</style>
