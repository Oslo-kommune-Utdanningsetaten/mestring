<script lang="ts">
  import { currentUser } from '../stores/data'
  import { login } from '../stores/auth'
  import ButtonMini from '../components/ButtonMini.svelte'
</script>

<div>
  <h2>Ukjent adresse</h2>
  <section class="mt-4">
    Eller som en klok person en gang sa: <span class="fst-italic">404 - not found.</span>
  </section>
  {#if !$currentUser}
    <section class="mt-4">
      Hvis dette vanligvis pleier å funke, hjelper det sikkert å logge inn.
      <div class="mt-4">
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
    </section>
  {/if}
</div>

<style>
</style>
