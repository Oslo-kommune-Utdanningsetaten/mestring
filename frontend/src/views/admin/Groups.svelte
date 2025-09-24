<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import type { GroupReadable, SchoolReadable } from '../../generated/types.gen'
  import { groupsList, schoolsList } from '../../generated/sdk.gen'
  import { urlStringFrom } from '../../utils/functions'
  import { dataStore } from '../../stores/data'
  import GroupTypeTag from '../../components/GroupTypeTag.svelte'

  const router = useTinyRouter()
  let groups = $state<GroupReadable[]>([])
  let schools = $state<SchoolReadable[]>([])
  let isLoadingSchools = $state<boolean>(false)
  let isLoadingGroups = $state<boolean>(false)
  let selectedSchool = $state<SchoolReadable | null>($dataStore.currentSchool)
  let nameFilter = $state<string>('')
  let filteredGroups = $derived(
    nameFilter
      ? groups.filter(group => group.displayName.toLowerCase().includes(nameFilter.toLowerCase()))
      : groups
  )

  let headerText = $derived.by(() => {
    let text = selectedSchool ? `Grupper ved ${selectedSchool.displayName}` : 'Alle grupper'
    text = nameFilter ? `${text} som inneholder "${nameFilter}"` : text
    return text
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

  const fetchGroups = async () => {
    if (!selectedSchool) return
    try {
      isLoadingGroups = true
      const result = await groupsList({ query: { school: selectedSchool.id } })
      groups = result.data || []
    } catch (error) {
      console.error('Error fetching groups:', error)
      groups = []
    } finally {
      isLoadingGroups = false
    }
  }

  const handleSchoolSelect = (schoolId: string): void => {
    console.log('Selected school ID:', schoolId)
    if (schoolId && schoolId !== '0') {
      router.navigate(urlStringFrom({ school: schoolId }, { path: '/admin/groups', mode: 'merge' }))
    } else {
      router.navigate('/admin/groups')
    }
  }

  $effect(() => {
    fetchSchools()
  })

  $effect(() => {
    const selectedSchoolId = router.getQueryParam('school')
    if (selectedSchoolId) {
      selectedSchool = schools.find(school => school.id === selectedSchoolId) || null
    } else {
      selectedSchool = null
    }
    if (selectedSchool && selectedSchool.id) {
      fetchGroups()
    }
  })
</script>

<section class="pt-3">
  <h2 class="py-3">{headerText}</h2>
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
      <input
        type="text"
        class="group-filter-input"
        placeholder="Navn på gruppe"
        bind:value={nameFilter}
      />
    {/if}
  </div>
</section>

<section class="py-3">
  {#if selectedSchool}
    <div class="card shadow-sm w-100">
      {#if isLoadingGroups}
        <div class="m-4">
          <div class="spinner-border text-primary" role="status"></div>
          <span>Henter grupper...</span>
        </div>
      {:else if filteredGroups.length === 0}
        <div class="m-4">Ingen grupper funnet</div>
      {:else}
        <!-- Header row -->
        <div class="group-grid-row header">
          <span>Gruppe</span>
          <span>Type</span>
          <span>Aktivert</span>
        </div>
        <!-- Data rows -->
        {#each filteredGroups as group}
          <div class="group-grid-row">
            <span>{group.displayName}</span>
            <GroupTypeTag {group} />
            <span>{group.isEnabled ? 'Ja' : 'Nei'}</span>
          </div>
        {/each}
      {/if}
    </div>
  {:else}
    Velg skole for å se grupper
  {/if}
</section>

<style>
  .group-filter-input {
    border: 2px solid var(--bs-primary);
    border-radius: 0;
    height: 48px;
    margin-top: 0px;
    padding-left: 15px;
    margin-left: 10px;
  }

  .group-grid-row {
    display: grid;
    grid-template-columns: 4fr 4fr 1fr;
    column-gap: 1rem;
    padding: 0.5rem 0.5rem;
    align-items: center;
    justify-items: start;
    border-bottom: 1px solid #dee2e6;
  }

  .group-grid-row.header {
    font-weight: bold;
    background-color: var(--bs-light);
    border-top-right-radius: inherit;
    border-top-left-radius: inherit;
    align-items: start;
  }
</style>
