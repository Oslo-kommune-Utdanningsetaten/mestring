<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import type { SchoolType } from '../../generated/types.gen'

  import { currentSchool } from '../../stores/data'

  import Offcanvas from '../../components/Offcanvas.svelte'
  import TranslationEdit from '../../components/edit/TranslationEdit.svelte'
  import ButtonMini from '../../components/ButtonMini.svelte'

  let schoolWip = $state<SchoolType | null>(null)
  let isEditorOpen = $state<boolean>(false)
  let school = $derived<SchoolType>($currentSchool)

  const handleDone = () => {
    schoolWip = null
    isEditorOpen = false
  }

  const handleEditTranslations = () => {
    if (school) {
      schoolWip = { ...school }
      isEditorOpen = true
    }
  }
</script>

<section class="py-4">
  {#if school}
    <h2 class="mb-3">Oversettelser for {school.displayName}</h2>

    <ButtonMini
      options={{
        title: school.uiTranslations ? 'Rediger oversettelser' : 'Legg til oversettelser',
        iconName: 'document-edit',
        skin: 'primary',
        variant: 'label-only',
        onClick: () => handleEditTranslations(),
      }}
    >
      {school.uiTranslations ? 'Rediger oversettelser' : 'Legg til oversettelser'}
    </ButtonMini>
    <div class="mt-4">
      {#if school.uiTranslations}
        <pre>{JSON.stringify(school.uiTranslations, null, 2)}</pre>
      {:else}
        <p class="text-muted">ingen oversettelser for denne skolen</p>
      {/if}
    </div>
  {/if}
</section>

<!-- Offcanvas for creating/editing mastery schemas -->
<Offcanvas
  bind:isOpen={isEditorOpen}
  width="80vw"
  ariaLabel="Rediger oversettelser"
  onClosed={() => {
    schoolWip = null
  }}
>
  {#if schoolWip}
    <TranslationEdit school={schoolWip} onDone={handleDone} />
  {/if}
</Offcanvas>

<style>
</style>
