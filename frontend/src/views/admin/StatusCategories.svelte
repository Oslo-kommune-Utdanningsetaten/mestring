<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import {
    statusCategoriesDestroy,
    statusCategoriesList,
    statusCategoriesPartialUpdate,
    schoolsList,
  } from '../../generated/sdk.gen'
  import type { StatusCategoryType, SchoolType } from '../../generated/types.gen'
  import { urlStringFrom } from '../../utils/functions'
  import { dataStore } from '../../stores/data'
  import { STATUS_CATEGORY_NAMES } from '../../utils/constants'
  import ButtonMini from '../../components/ButtonMini.svelte'
  import Offcanvas from '../../components/Offcanvas.svelte'
  import StatusCategoryEdit from '../../components/StatusCategoryEdit.svelte'

  const router = useTinyRouter()
  let statusCategoryWip = $state<Partial<StatusCategoryType> | null>(null)
  let isEditorOpen = $state<boolean>(false)
  let schools = $state<SchoolType[]>([])
  let isLoadingSchools = $state<boolean>(false)
  let statusCategories = $derived<StatusCategoryType[]>([])
  let selectedSchool = $derived.by(() => {
    const schoolIdFromUrl = router.getQueryParam('school')
    return schools.find(s => s.id === schoolIdFromUrl) || $dataStore.currentSchool
  })
  let masterySchemas = $derived($dataStore.masterySchemas)

  const fetchSchools = async () => {
    try {
      const result = await schoolsList({})
      schools = result.data || []
    } catch (error) {
      console.error('Error fetching schools:', error)
      schools = []
    }
  }

  const fetchStatusCategories = async () => {
    const query = { school: selectedSchool.id }
    try {
      const result = await statusCategoriesList({ query })
      statusCategories = result.data || []
    } catch (error) {
      console.error('Error fetching status categories:', error)
      statusCategories = []
    }
  }

  const handleSchoolSelect = (schoolId: string): void => {
    if (schoolId && schoolId !== '0') {
      router.navigate(
        urlStringFrom({ school: schoolId }, { path: '/admin/status-categories', mode: 'merge' })
      )
    } else {
      router.navigate('/admin/status-categories')
    }
  }

  const handleDone = () => {
    isEditorOpen = false
    fetchStatusCategories()
  }

  const handleNewStatusCategory = () => {
    statusCategoryWip = {
      schoolId: selectedSchool?.id,
      isEnabled: true,
    }
    isEditorOpen = true
  }

  const handleEditStatusCategory = (statusCategory: StatusCategoryType | null) => {
    statusCategoryWip = { ...statusCategory }
    isEditorOpen = true
  }

  const handleCopyStatusCategory = (statusCategory: StatusCategoryType | null) => {
    statusCategoryWip = {
      ...statusCategory,
      id: undefined,
      title: 'KOPI: ' + statusCategory?.title,
    }
    isEditorOpen = true
  }

  const handleDeleteStatusCategory = async (statusCategoryId: string) => {
    try {
      await statusCategoriesDestroy({
        path: { id: statusCategoryId },
      })
    } catch (error) {
      console.error('Error deleting status category:', error)
    } finally {
      await fetchStatusCategories()
    }
  }

  const toggleIsEnabled = async (statusCategory: StatusCategoryType) => {
    try {
      const current = statusCategory.isEnabled ?? false
      await statusCategoriesPartialUpdate({
        path: { id: statusCategory.id },
        body: { isEnabled: !current },
      })
    } catch (error) {
      console.error('Error updating isEnabled:', error)
    } finally {
      await fetchStatusCategories()
    }
  }

  $effect(() => {
    fetchSchools()
  })

  $effect(() => {
    if (selectedSchool && selectedSchool.id) {
      fetchStatusCategories()
    }
  })
</script>

<section class="pt-3">
  <h2 class="mb-4">Status categories</h2>
  <!-- Filter groups -->
  {#if isLoadingSchools}
    <div class="m-4">
      <div class="spinner-border text-primary" role="status"></div>
      <span>Henter skoler...</span>
    </div>
  {:else}
    <div class="filters-container">
      <div class="filter-item">
        <label for="schoolSelect" class="mb-1 visually-hidden">Velg skole:</label>
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
        title: 'Ny statuskategori',
        iconName: 'plus-sign',
        skin: 'primary',
        variant: 'label-only',
        classes: '',
        onClick: () => handleNewStatusCategory(),
      }}
    >
      Nytt mestringsskjema
    </ButtonMini>

    {#if statusCategories.length > 0 && !statusCategories.some(schema => schema.isEnabled)}
      <div class="alert alert-warning mt-4">
        Ingen av mestringsskjemaene for denne skolen er satt til enabled.
      </div>
    {/if}

    <div class="mt-4">
      {#if statusCategories.length > 0}
        {#each statusCategories as statusCategory}
          <div class="card shadow-sm">
            <div class="card-body">
              <h3 class="card-title">
                {statusCategory.title}
              </h3>
              <p>
                Mastery schema: {masterySchemas.find(ms => ms.id === statusCategory.masterySchemaId)
                  .title || '?'}
              </p>
              <p>
                Name: {STATUS_CATEGORY_NAMES[statusCategory.name]} ({statusCategory.name})
              </p>

              <div class="mb-4">
                <pkt-checkbox
                  label={statusCategory.isEnabled ? 'Currently enabled' : 'Currently disabled'}
                  labelPosition="right"
                  isSwitch="true"
                  aria-checked={statusCategory.isEnabled}
                  checked={statusCategory.isEnabled}
                  onchange={() => toggleIsEnabled(statusCategory)}
                ></pkt-checkbox>
              </div>

              <ButtonMini
                options={{
                  title: 'Rediger',
                  iconName: 'edit',
                  skin: 'secondary',
                  variant: 'icon-left',
                  classes: 'my-2 me-2',
                  onClick: () => handleEditStatusCategory(statusCategory),
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
                  onClick: () => handleCopyStatusCategory(statusCategory),
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
                  onClick: () => handleDeleteStatusCategory(statusCategory.id),
                }}
              >
                Slett
              </ButtonMini>
            </div>
          </div>
        {/each}
      {:else}
        <div class="alert alert-info">Ingen statuskategorier for denne skolen</div>
      {/if}
    </div>
  {:else}
    <div class="alert alert-info">Velg en skole</div>
  {/if}
</section>

<!-- Offcanvas for creating/editing status categories -->
<Offcanvas
  bind:isOpen={isEditorOpen}
  width="80vw"
  ariaLabel="Rediger statuskategori"
  onClosed={() => {
    statusCategoryWip = null
    fetchStatusCategories()
  }}
>
  {#if statusCategoryWip}
    <StatusCategoryEdit statusCategory={statusCategoryWip} onDone={handleDone} />
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
