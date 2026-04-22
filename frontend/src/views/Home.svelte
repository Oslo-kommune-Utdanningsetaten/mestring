<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import { currentUser } from '../stores/data'
  import { login } from '../stores/auth'
  import GroupsCompact from './GroupsCompact.svelte'
  import ObservationsTeacherView from '../components/ObservationsTeacherView.svelte'
  import ButtonMini from '../components/ButtonMini.svelte'

  const router = useTinyRouter()
  const errorFromUrl = $derived(router.getQueryParam('error'))
</script>

{#if $currentUser}
  <GroupsCompact />
  {#if $currentUser.isTeacher || $currentUser.isSuperadmin}
    <ObservationsTeacherView />
  {/if}
  {#if $currentUser.isStudent}
    Yo a student?
  {/if}
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
