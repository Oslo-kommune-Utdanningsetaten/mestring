<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import {
    masterySchemasDestroy,
    masterySchemasList,
    schoolsList,
    masterySchemasPartialUpdate,
  } from '../../generated/sdk.gen'
  import type { MasterySchemaType, SchoolType } from '../../generated/types.gen'
  import type { MasterySchemaWithConfig } from '../../types/models'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { urlStringFrom } from '../../utils/functions'
  import ButtonMini from '../../components/ButtonMini.svelte'
  import MasterySchemaEdit from '../../components/MasterySchemaEdit.svelte'
  import Offcanvas from '../../components/Offcanvas.svelte'
  import { dataStore } from '../../stores/data'

  const router = useTinyRouter()
  let masterySchemaWip: Partial<MasterySchemaWithConfig> | null =
    $state<Partial<MasterySchemaType> | null>(null)
  let isJsonVisible = $state<boolean>(false)
  let isEditorOpen = $state<boolean>(false)
  let schools = $state<SchoolType[]>([])
  let isLoadingSchools = $state<boolean>(false)
  let selectedSchool = $state<SchoolType | null>(null)
  let masterySchemas = $derived<MasterySchemaWithConfig[]>([])

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

  const handleEditMasterySchema = (masterySchema: MasterySchemaType | null) => {
    if (masterySchema) {
      masterySchemaWip = { ...masterySchema }
    } else {
      masterySchemaWip = selectedSchool ? { schoolId: selectedSchool.id } : {}
    }
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

  $effect(() => {
    const schoolId = router.getQueryParam('school') || null
    fetchSchools().then(() => {
      selectedSchool = schools.find(school => school.id === schoolId) || null
      fetchMasterySchemas()
    })
  })

  $effect(() => {
    if ($dataStore.currentSchool && !selectedSchool) {
      router.navigate(
        urlStringFrom(
          { school: $dataStore.currentSchool.id },
          { path: '/admin/mastery-schemas', mode: 'merge' }
        )
      )
    }
  })
</script>

<section class="pt-3">
  <h2 class="mb-4">Mastery Schemas</h2>
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
    {#if selectedSchool}
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
                <pkt-checkbox
                  label={masterySchema.isDefault ? 'Default schema for school' : 'Not default'}
                  labelPosition="right"
                  isSwitch="true"
                  aria-checked={masterySchema.isDefault}
                  checked={masterySchema.isDefault}
                  onchange={() => toggleIsDefault(masterySchema)}
                ></pkt-checkbox>
              </div>

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
        <div class="alert alert-info">Ingen mestringsskjemaer for denne skolen</div>
      {/if}
    {:else}
      <div class="alert alert-info">Velg en skole</div>
    {/if}
  </div>
</section>

<!-- Offcanvas for creating/editing mastery schemas -->
<Offcanvas
  bind:isOpen={isEditorOpen}
  width="70vw"
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
