<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import {
    masterySchemasDestroy,
    masterySchemasList,
    schoolsList,
    masterySchemasPartialUpdate,
  } from '../../generated/sdk.gen'
  import type { MasterySchemaType, SchoolType } from '../../generated/types.gen'
  import type { MasterySchemaWithConfig, MasteryConfigLevel } from '../../types/models'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { urlStringFrom, getContrastFriendlyTextColor } from '../../utils/functions'
  import { VALUE_INPUT_VARIANTS } from '../../utils/constants'
  import { dataStore } from '../../stores/data'
  import { useMasteryCalculations } from '../../utils/masteryHelpers'
  import ButtonMini from '../../components/ButtonMini.svelte'
  import Offcanvas from '../../components/Offcanvas.svelte'
  import MasterySchemaEdit from '../../components/MasterySchemaEdit.svelte'

  const router = useTinyRouter()
  let masterySchemaWip: Partial<MasterySchemaWithConfig> | null =
    $state<Partial<MasterySchemaType> | null>(null)
  let isJsonVisible = $state<boolean>(false)
  let isEditorOpen = $state<boolean>(false)
  let schools = $state<SchoolType[]>([])
  let isLoadingSchools = $state<boolean>(false)
  let masterySchemas = $derived<MasterySchemaWithConfig[]>([])
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

  const fetchMasterySchemas = async () => {
    const query = selectedSchool ? { school: selectedSchool.id } : {}
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
    isEditorOpen = false
    fetchMasterySchemas()
  }

  const handleNewMasterySchema = () => {
    masterySchemaWip = { schoolId: selectedSchool?.id }
    isEditorOpen = true
  }

  const handleEditMasterySchema = (masterySchema: MasterySchemaType | null) => {
    masterySchemaWip = { ...masterySchema }
    isEditorOpen = true
  }

  const handleCopyMasterySchema = (masterySchema: MasterySchemaType | null) => {
    masterySchemaWip = { ...masterySchema }
    delete masterySchemaWip.id
    masterySchemaWip.title = 'KOPI: ' + masterySchemaWip.title
    isEditorOpen = true
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

  // Toggle whether group title is displayed in goal edit
  const toggleIsDefault = async (masterySchema: MasterySchemaType) => {
    try {
      const current = masterySchema.isDefault ?? false
      const result = await masterySchemasPartialUpdate({
        path: { id: masterySchema.id },
        body: { isDefault: !current },
      })
      const otherSchemasForSchool = masterySchemas.filter(
        schema => schema.schoolId === selectedSchool?.id && schema.id !== masterySchema.id
      )
      // If setting this schema to default, unset others
      if (result.data?.isDefault) {
        for (const schema of otherSchemasForSchool) {
          await masterySchemasPartialUpdate({
            path: { id: schema.id },
            body: { isDefault: false },
          })
        }
      }
    } catch (error) {
      console.error('Error updating isGoalTitleEnabled:', error)
    } finally {
      // sleep a bit to allow backend to process changes
      await new Promise(resolve => setTimeout(resolve, 0.6))
      await fetchMasterySchemas()
    }
  }

  const getSchoolName = (schoolId: string | undefined) => {
    return schools.find(school => school.id === schoolId)?.displayName || '??'
  }

  const getMasteryLevelsSummary = (masterySchema: MasterySchemaWithConfig) => {
    const calculations = useMasteryCalculations(masterySchema)
    return calculations.minValue + ' - ' + calculations.maxValue
  }

  $effect(() => {
    fetchSchools()
  })

  $effect(() => {
    if (selectedSchool && selectedSchool.id) {
      fetchMasterySchemas()
    }
  })
</script>

<section class="pt-3">
  <h2 class="mb-4">Mastery Schemas</h2>
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
    <ButtonMini
      options={{
        title: 'Nytt mestringsskjema',
        iconName: 'plus-sign',
        skin: 'primary',
        variant: 'label-only',
        classes: '',
        onClick: () => handleNewMasterySchema(),
      }}
    >
      Nytt mestringsskjema
    </ButtonMini>

    <p>Input variants: {VALUE_INPUT_VARIANTS.join(', ')}</p>

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
              <p>
                {masterySchema.description || 'Ingen beskrivelse'}
              </p>
              <p class="text-muted">
                Range: {getMasteryLevelsSummary(masterySchema)}
                <br />
                Input: {masterySchema.config.valueInput}
                <br />
                ID: {masterySchema.id}
                <br />
              </p>

              <div class="mb-4">
                <pkt-checkbox
                  label={masterySchema.isDefault ? 'Default schema for school' : 'Not default'}
                  labelPosition="right"
                  isSwitch="true"
                  aria-checked={masterySchema.isDefault}
                  checked={masterySchema.isDefault}
                  onchange={() => toggleIsDefault(masterySchema)}
                ></pkt-checkbox>
              </div>

              <div class="mb-4 d-flex gap-2">
                {#each masterySchema?.config?.levels || [] as level}
                  <div class="d-flex flex-column align-items-center">
                    <span
                      class="p-2 w-100 text-center"
                      style="background-color: {level.color ||
                        'white'}; color: {getContrastFriendlyTextColor(level.color)};"
                    >
                      {level.title}
                    </span>
                    <span class="small text-muted py-1 bg-light w-100 text-center">
                      {level.minValue}&nbsp;➡&nbsp;{level.maxValue}
                    </span>
                  </div>
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
                  title: 'Kopier',
                  iconName: 'copy',
                  skin: 'secondary',
                  variant: 'icon-left',
                  classes: 'my-2 me-2',
                  onClick: () => handleCopyMasterySchema(masterySchema),
                }}
              >
                Kopier
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
        <div class="alert alert-info">Ingen mestringsskjemaer for denne skolen</div>
      {/if}
    </div>
  {:else}
    <div class="alert alert-info">Velg en skole</div>
  {/if}
</section>

<!-- Offcanvas for creating/editing mastery schemas -->
<Offcanvas
  bind:isOpen={isEditorOpen}
  width="80vw"
  ariaLabel="Rediger mestringsskjema"
  onClosed={() => {
    masterySchemaWip = null
    fetchMasterySchemas()
  }}
>
  {#if masterySchemaWip}
    <MasterySchemaEdit masterySchema={masterySchemaWip} onDone={handleDone} />
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
