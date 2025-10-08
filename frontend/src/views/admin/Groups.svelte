<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import type { GroupReadable, SchoolReadable, SubjectReadable } from '../../generated/types.gen'
  import { groupsList, schoolsList, groupsUpdate } from '../../generated/sdk.gen'
  import { urlStringFrom } from '../../utils/functions'
  import { dataStore } from '../../stores/data'
  import GroupTypeTag from '../../components/GroupTypeTag.svelte'

  const router = useTinyRouter()
  let groups = $state<GroupReadable[]>([])
  let schools = $state<SchoolReadable[]>([])
  let isLoadingSchools = $state<boolean>(false)
  let isLoadingGroups = $state<boolean>(false)
  let groupFetchSelection = $state<string>('all') // all, only-enabled, only-disabled
  let selectedSchool = $state<SchoolReadable | null>(null)
  let nameFilter = $state<string>('')

  // Radio options for group filtering
  const groupFetchOptions = [
    { value: 'all', label: 'Alle grupper' },
    { value: 'only-enabled', label: 'Aktiverte grupper' },
    { value: 'only-disabled', label: 'Deaktiverte grupper' },
  ] as const

  let filteredGroups = $derived(
    nameFilter
      ? groups.filter(group => group.displayName.toLowerCase().includes(nameFilter.toLowerCase()))
      : groups
  )

  let groupFetchOption = $derived(
    groupFetchSelection === 'all'
      ? {}
      : groupFetchSelection === 'only-enabled'
        ? { isEnabled: true }
        : { isEnabled: false }
  )

  const subjectsById: Record<string, SubjectReadable> = $derived(
    $dataStore.subjects.reduce(
      (acc, subject) => {
        acc[subject.id] = subject
        return acc
      },
      {} as Record<string, SubjectReadable>
    )
  )

  let headerText = $derived.by(() => {
    let text = selectedSchool ? `Grupper ved ${selectedSchool.displayName}` : 'Alle grupper'
    text = nameFilter ? `${text} som inneholder "${nameFilter}"` : text
    return text
  })

  const getSubjectForGroup = (group: GroupReadable): string => {
    const subject = group.subjectId ? subjectsById[group.subjectId] : null
    return subject?.displayName || ''
  }

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
      const queryOption = { ...groupFetchOption, school: selectedSchool.id }
      const result = await groupsList({ query: queryOption })
      groups = (result.data || []).sort((a, b) =>
        a.displayName.localeCompare(b.displayName, 'no', { sensitivity: 'base' })
      )
    } catch (error) {
      console.error('Error fetching groups:', error)
      groups = []
    } finally {
      isLoadingGroups = false
    }
  }

  const handleSchoolSelect = (schoolId: string): void => {
    if (schoolId && schoolId !== '0') {
      router.navigate(urlStringFrom({ school: schoolId }, { path: '/admin/groups', mode: 'merge' }))
    } else {
      router.navigate('/admin/groups')
    }
  }

  const handleGroupTypeToggle = async (group: GroupReadable) => {
    const currentTypeName = group.type === 'basis' ? 'Basisgruppe' : 'Undervisningsgruppe'
    const newTypeName = group.type === 'basis' ? 'Undervisningsgruppe' : 'Basisgruppe'

    const confirmed = confirm(
      `Er du sikker på at du vil endre gruppe ${group.displayName} fra ${currentTypeName} til ${newTypeName}?`
    )

    if (!confirmed) {
      // Refetch to flip back radio buttons
      fetchGroups()
      return
    }

    const newType = group.type === 'basis' ? 'teaching' : 'basis'
    try {
      await groupsUpdate({
        path: { id: group.id },
        body: { ...group, type: newType } as GroupReadable,
      })
      fetchGroups()
    } catch (error) {
      console.error('Error toggling group type:', error)
    }
  }

  const handleToggleGroupEnabledStatus = async (group: GroupReadable) => {
    try {
      await groupsUpdate({
        path: { id: group.id },
        body: { ...group, isEnabled: !group.isEnabled } as GroupReadable,
      })
    } catch (error) {
      console.error('Error toggling group endabled status:', error)
    } finally {
      fetchGroups()
    }
  }

  $effect(() => {
    fetchSchools()
  })

  $effect(() => {
    if (!router.getQueryParam('school') && $dataStore.currentSchool) {
      handleSchoolSelect($dataStore.currentSchool.id)
    }
  })

  $effect(() => {
    const schoolIdFromUrl = router.getQueryParam('school')
    const nextSchool = schoolIdFromUrl
      ? (schools.find(school => school.id === schoolIdFromUrl) ?? null)
      : null
    // Only assign school if it changed
    if (nextSchool?.id !== selectedSchool?.id) {
      selectedSchool = nextSchool
    }
  })

  $effect(() => {
    if (selectedSchool) {
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
  <!-- Radio buttons for filtering groups -->
  <fieldset>
    <legend class="visually-hidden">Filtrer grupper</legend>
    {#each groupFetchOptions as option}
      <label class="my-2 ms-1 d-block">
        <input
          type="radio"
          name="groupFetchInclusion"
          value={option.value}
          bind:group={groupFetchSelection}
        />
        <span class="ms-2">{option.label}</span>
      </label>
    {/each}
  </fieldset>
</section>

<pre>{JSON.stringify(
    $dataStore.subjects?.map(s => s.displayName),
    null,
    2
  )}</pre>

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
          <span>Fag</span>
          <span>Aktivert</span>
        </div>
        <!-- Data rows -->
        {#each filteredGroups as group}
          <div class="group-grid-row">
            <span>{group.displayName}</span>
            <GroupTypeTag
              {group}
              onclick={() => handleGroupTypeToggle(group)}
              isTypeWarningEnabled={true}
            />
            <span>
              {#if group.type === 'basis'}
                {getSubjectForGroup(group)}
              {:else}
                {getSubjectForGroup(group)}
              {/if}
            </span>
            <pkt-checkbox
              label="Aktivert"
              labelPosition="hidden"
              isSwitch="true"
              aria-checked={group.isEnabled}
              checked={group.isEnabled}
              onchange={() => handleToggleGroupEnabledStatus(group)}
            ></pkt-checkbox>
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
    grid-template-columns: 2fr 2fr 1fr 0.5fr;
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
    align-items: center;
  }
</style>
