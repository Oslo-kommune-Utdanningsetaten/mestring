<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import type { MasterySchemaType, SchoolType } from '../../generated/types.gen'

  import { schoolsList } from '../../generated/sdk.gen'
  import { urlStringFrom } from '../../utils/functions'
  import { dataStore } from '../../stores/data'

  import Offcanvas from '../../components/Offcanvas.svelte'
  import TranslationEdit from '../../components/edit/TranslationEdit.svelte'
  import ButtonMini from '../../components/ButtonMini.svelte'

  const router = useTinyRouter()
  let schools = $state<SchoolType[]>([])
  let isLoadingSchools = $state<boolean>(false)

  let schoolWip = $state<SchoolType | null>(null)
  let isEditorOpen = $state<boolean>(false)

  let selectedSchool = $derived.by(() => {
    const schoolIdFromUrl = router.getQueryParam('school')
    return schools.find(s => s.id === schoolIdFromUrl) || $dataStore.currentSchool
  })

  const fetchSchools = async () => {
    try {
      const result = await schoolsList({})
      schools = result.data || []
    } catch (error) {
      console.error('Error fetching schools:', error)
      schools = []
    }
  }

  const handleSchoolSelect = (schoolId: string): void => {
    if (schoolId && schoolId !== '0') {
      router.navigate(
        urlStringFrom({ school: schoolId }, { path: '/admin/translations', mode: 'merge' })
      )
    } else {
      router.navigate('/admin/translations')
    }
  }

  const handleDone = () => {
    schoolWip = null
    isEditorOpen = false
    fetchSchools()
  }

  const handleEditTranslations = () => {
    schoolWip = { ...selectedSchool }
    isEditorOpen = true
  }

  $effect(() => {
    fetchSchools()
  })
</script>

<section class="pt-3">
  <h2 class="mb-4">Translations</h2>

  <!-- Filter groups -->
  {#if isLoadingSchools}
    <div class="m-4">
      <div class="spinner-border text-primary" role="status"></div>
      <span>Henter skoler...</span>
    </div>
  {:else}
    <div class="filters-container">
      <div class="filter-item">
        <label for="schoolSelect" class="mb-1 visually-hidden">Filtrer på skole:</label>
        <select
          class="pkt-input"
          id="schoolSelect"
          onchange={(e: Event) => handleSchoolSelect((e.target as HTMLSelectElement).value)}
        >
          {#each schools as school}
            <option value={school.id} selected={school.id === selectedSchool?.id}>
              {school.displayName}
            </option>
          {/each}
        </select>
      </div>
    </div>
  {/if}
</section>

<section class="py-4">
  {#if selectedSchool}
    <h3>Oversettelser for {selectedSchool.displayName}</h3>
    <pre>{JSON.stringify(selectedSchool.uiTranslations, null, 2)}</pre>
  {/if}

  <ButtonMini
    options={{
      title: 'Rediger oversettelser',
      iconName: 'document-edit',
      skin: 'primary',
      variant: 'label-only',
      classes: '',
      onClick: () => handleEditTranslations(),
    }}
  >
    Rediger oversettelser
  </ButtonMini>
</section>

<!-- Offcanvas for creating/editing mastery schemas -->
<Offcanvas
  bind:isOpen={isEditorOpen}
  width="80vw"
  ariaLabel="Rediger oversettelser"
  onClosed={() => {
    schoolWip = null
    fetchSchools()
  }}
>
  {#if schoolWip}
    <TranslationEdit school={schoolWip} onDone={handleDone} />
  {/if}
</Offcanvas>

<style>
  .filters-container {
    display: flex;
    gap: 1rem;
    align-items: flex-end;
  }

  .filter-item {
    display: flex;
    flex-direction: column;
    flex: 1 1 20rem;
    min-width: 3rem;
    max-width: 25rem;
  }
</style>
