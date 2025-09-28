<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { masterySchemasDestroy, masterySchemasList, schoolsList } from '../../generated/sdk.gen'
  import type { MasterySchemaReadable, SchoolReadable } from '../../generated/types.gen'
  import type { MasterySchemaWithConfig } from '../../types/models'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { urlStringFrom } from '../../utils/functions'
  import ButtonMini from '../../components/ButtonMini.svelte'
  import MasterySchemaEdit from '../../components/MasterySchemaEdit.svelte'

  const router = useTinyRouter()
  let masterySchemas = $derived<MasterySchemaWithConfig[]>([])
  let masterySchemaWip: Partial<MasterySchemaWithConfig> | null =
    $state<Partial<MasterySchemaReadable> | null>(null)
  let isJsonVisible = $state<boolean>(false)
  let schools = $state<SchoolReadable[]>([])
  let isLoadingSchools = $state<boolean>(false)
  let selectedSchool = $derived<SchoolReadable | null>(null)

  const fetchSchools = async () => {
    try {
      const result = await schoolsList({})
      schools = result.data || []
    } catch (error) {
      console.error('Error fetching schools:', error)
      schools = []
    }
  }

  const fetchMasterySchemas = async () => {
    const query = selectedSchool ? { school: selectedSchool.id } : {}
    console.log('fetchMasterySchemas with query', query)
    const result = await masterySchemasList({ query })
    masterySchemas = result.data || []
  }

  const handleSchoolSelect = (schoolId: string): void => {
    if (schoolId && schoolId !== '0') {
      router.navigate(
        urlStringFrom({ school: schoolId }, { path: '/admin/mastery-schemas', mode: 'merge' })
      )
    } else {
      router.navigate('/admin/mastery-schemas')
    }
  }

  const handleDone = () => {
    masterySchemaWip = null
    fetchMasterySchemas()
  }

  const handleEditMasterySchema = (masterySchema: MasterySchemaReadable | null) => {
    if (masterySchema) {
      masterySchemaWip = { ...masterySchema }
    } else {
      masterySchemaWip = selectedSchool ? { schoolId: selectedSchool.id } : {}
    }
  }

  const handleDeleteMasterySchema = async (masterySchemaId: string) => {
    try {
      await masterySchemasDestroy({
        path: { id: masterySchemaId },
      })
    } catch (error) {
      console.error('Error deleting schema:', error)
    } finally {
      await fetchMasterySchemas()
    }
  }

  const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      if (masterySchemaWip) {
        handleDone()
      }
    }
  }

  const getSchoolName = (schoolId: string | undefined) => {
    return schools.find(school => school.id === schoolId)?.displayName || '??'
  }

  $effect(() => {
    const schoolId = router.getQueryParam('school') || null
    fetchSchools().then(() => {
      selectedSchool = schools.find(school => school.id === schoolId) || null
      fetchMasterySchemas()
    })
  })
</script>

<section class="pt-3">
  <h1 class="mb-4">Mastery Schemas</h1>
  <!-- Filter groups -->
  <div class="d-flex align-items-center gap-2">
    {#if isLoadingSchools}
      <div class="m-4">
        <div class="spinner-border text-primary" role="status"></div>
        <span>Henter skoler...</span>
      </div>
    {:else}
      <div class="pkt-inputwrapper">
        <select
          class="pkt-input"
          id="groupSelect"
          onchange={(e: Event) => handleSchoolSelect((e.target as HTMLSelectElement).value)}
        >
          <option value="0" selected={!selectedSchool?.id}>Velg skole</option>
          {#each schools as school}
            <option value={school.id} selected={school.id === selectedSchool?.id}>
              {school.displayName}
            </option>
          {/each}
        </select>
      </div>
    {/if}
  </div>
</section>

<section class="py-4">
  <ButtonMini
    options={{
      title: 'Nytt mestringsskjema',
      iconName: 'plus-sign',
      skin: 'primary',
      variant: 'label-only',
      classes: '',
      onClick: () => handleEditMasterySchema(null),
    }}
  >
    Nytt mestringsskjema
  </ButtonMini>

  <div class="pkt-input-check mt-3">
    <div class="pkt-input-check__input">
      <input
        class="pkt-input-check__input-checkbox"
        type="checkbox"
        role="switch"
        id="groupTypeSwitch"
        bind:checked={isJsonVisible}
      />
      <label class="pkt-input-check__input-label" for="groupTypeSwitch">Vis JSON config</label>
    </div>
  </div>

  <div class="mt-4">
    {#if masterySchemas.length > 0}
      {#each masterySchemas as masterySchema}
        <div class="card shadow-sm">
          <div class="card-body">
            <h3 class="card-title">
              {masterySchema.title}
            </h3>
            <h5 class="card-title">
              {getSchoolName(masterySchema.schoolId)}
            </h5>
            <p class="card-text">
              {masterySchema.description || 'Ingen beskrivelse'}
            </p>

            <div class="mb-4">
              {#each masterySchema?.config?.levels || [] as level}
                <span class="p-2" style="background-color: {level.color || 'white'};">
                  {level.title}
                </span>
              {/each}
            </div>

            {#if isJsonVisible}
              <div class="json-viewer">
                <pre>{JSON.stringify(masterySchema, null, 2)}</pre>
              </div>
            {/if}

            <ButtonMini
              options={{
                title: 'Rediger',
                iconName: 'edit',
                skin: 'secondary',
                variant: 'icon-left',
                classes: 'my-2 me-2',
                onClick: () => handleEditMasterySchema(masterySchema),
              }}
            >
              Rediger
            </ButtonMini>

            <ButtonMini
              options={{
                title: 'Slett',
                iconName: 'trash-can',
                skin: 'secondary',
                variant: 'icon-left',
                classes: 'my-2',
                onClick: () => handleDeleteMasterySchema(masterySchema.id),
              }}
            >
              Slett
            </ButtonMini>
          </div>
        </div>
      {/each}
    {:else}
      <div class="alert alert-info">No mastery schemas available for the selected school.</div>
    {/if}
  </div>
</section>

<svelte:window on:keydown={handleKeydown} />

<!-- offcanvas for creating/editing goals -->
<div class="offcanvas-edit custom-offcanvas-edit shadow-sm" class:visible={!!masterySchemaWip}>
  <MasterySchemaEdit masterySchema={masterySchemaWip} onDone={handleDone} />
</div>

<style>
  .custom-offcanvas-edit {
    right: -70vw;
    width: 70vw;
    overflow-y: auto;
  }
</style>
