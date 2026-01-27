<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import type { GroupType, SchoolType, SubjectType } from '../../generated/types.gen'
  import { groupsList, schoolsList, groupsUpdate } from '../../generated/sdk.gen'
  import { urlStringFrom } from '../../utils/functions'
  import { dataStore } from '../../stores/data'
  import GroupTag from '../../components/GroupTag.svelte'
  import ButtonIcon from '../../components/ButtonIcon.svelte'
  import { NONE_FIELD_VALUE } from '../../utils/constants'

  const router = useTinyRouter()
  let groups = $state<GroupType[]>([])
  let schools = $state<SchoolType[]>([])
  let isLoadingSchools = $state<boolean>(false)
  let isLoadingGroups = $state<boolean>(false)
  let enabledSelection = $state<'include' | 'only' | 'exclude'>('only')
  let deletedSelection = $state<'include' | 'only' | 'exclude'>('include')
  let selectedSchool = $state<SchoolType | null>(null)
  let nameFilter = $state<string>('')
  let openRows = $state<Record<string, boolean>>({})

  // Options for filtering by enabled
  const enabledOptions = [
    { value: 'include', label: 'All' },
    { value: 'only', label: 'Enabled groups' },
    { value: 'exclude', label: 'Disabled groups' },
  ] as const

  // Options for filtering by deleted
  const deletedOptions = [
    { value: 'include', label: 'All' },
    { value: 'only', label: 'Deleted' },
    { value: 'exclude', label: 'Non-deleted' },
  ] as const

  let filteredGroups = $derived(
    nameFilter
      ? groups.filter(group => group.displayName.toLowerCase().includes(nameFilter.toLowerCase()))
      : groups
  )

  let groupFetchOptions = $derived({
    enabled: enabledSelection,
    deleted: deletedSelection,
  })

  const subjectsById: Record<string, SubjectType> = $derived(
    $dataStore.subjects.reduce(
      (acc, subject) => {
        acc[subject.id] = subject
        return acc
      },
      {} as Record<string, SubjectType>
    )
  )

  // Subjects available for the currently selected school (if subjects are school scoped)
  const subjectsForSelectedSchool = $derived(
    (() => {
      const currentSchoolId = selectedSchool?.id
      if (!currentSchoolId) return []
      return $dataStore.subjects
        .filter(s => {
          const subjSchoolId = (s as any).schoolId
          return subjSchoolId ? subjSchoolId === currentSchoolId : true
        })
        .sort((a, b) => a.displayName.localeCompare(b.displayName, 'no', { sensitivity: 'base' }))
    })()
  )

  let headerText = $derived.by(() => {
    let text = selectedSchool ? `Grupper ved ${selectedSchool.displayName}` : 'Alle grupper'
    text = nameFilter ? `${text} som inneholder "${nameFilter}"` : text
    return text
  })

  const getSubjectForGroup = (group: GroupType): string => {
    if (!group.subjectId) return 'ikke valgt'
    const subject = subjectsById[group.subjectId] || null
    return subject?.displayName || `skolen har ikke fag ${group.subjectId}`
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
      const queryOption = { ...groupFetchOptions, school: selectedSchool.id }
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

  const handleGroupTypeToggle = async (group: GroupType) => {
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
        body: { ...group, type: newType } as GroupType,
      })
      fetchGroups()
    } catch (error) {
      console.error('Error toggling group type:', error)
    }
  }

  const handleToggleGroupEnabledStatus = async (group: GroupType) => {
    try {
      await groupsUpdate({
        path: { id: group.id },
        body: { ...group, isEnabled: !group.isEnabled } as GroupType,
      })
    } catch (error) {
      console.error('Error toggling group endabled status:', error)
    } finally {
      fetchGroups()
    }
  }

  const handleGroupUpdate = async (
    group: GroupType,
    newFieldsAndValues: Partial<GroupType>
  ): Promise<void> => {
    try {
      const updatedGroup: GroupType = { ...group, ...newFieldsAndValues }
      await groupsUpdate({
        path: { id: group.id },
        body: updatedGroup,
      })
    } catch (error) {
      console.error('Error updating group subject:', error)
    } finally {
      fetchGroups()
    }
  }

  const handleInfoToggle = (groupId: string) => {
    openRows[groupId] = !openRows[groupId]
    openRows = { ...openRows }
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
      <div>
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
  <!-- Radio buttons for enabled status -->
  <div class="d-flex flex-wrap gap-3 mt-3">
    <fieldset class="border p-3 rounded">
      <legend class="w-auto fs-6">Enabled?</legend>
      {#each enabledOptions as option}
        <label class="my-2 ms-1 d-block">
          <input
            type="radio"
            name="enabledOptions"
            value={option.value}
            bind:group={enabledSelection}
          />
          <span class="ms-2">{option.label}</span>
        </label>
      {/each}
    </fieldset>

    <!-- Radio buttons for deleted status -->
    <fieldset class="border p-3 rounded">
      <legend class="w-auto fs-6">Deleted?</legend>
      {#each deletedOptions as option}
        <label class="my-2 ms-1 d-block">
          <input
            type="radio"
            name="deletedOptions"
            value={option.value}
            bind:group={deletedSelection}
          />
          <span class="ms-2">{option.label}</span>
        </label>
      {/each}
    </fieldset>
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
          <span>Display Name</span>
          <span>Type</span>
          <span>Subject</span>
          <span>Enabled</span>
          <span>JSON</span>
        </div>
        <!-- Data rows -->
        {#each filteredGroups as group (group.id)}
          <div class="group-grid-row">
            <a href="/groups/{group.id}">
              {group.displayName}
            </a>
            <GroupTag
              {group}
              title="Endre gruppetype"
              onclick={() => handleGroupTypeToggle(group)}
              isTypeWarningEnabled={true}
              isGroupNameEnabled={false}
              isGroupTypeNameEnabled={true}
            />
            <span>
              {#if group.type === 'basis'}
                <select
                  class="pkt-input"
                  id="subjectsAllowedSelect"
                  onchange={(e: Event) => {
                    const target = e.target as HTMLSelectElement | null
                    const changes = {
                      subjectId: target?.value === NONE_FIELD_VALUE ? null : target?.value,
                    }
                    handleGroupUpdate(group, changes)
                  }}
                >
                  <option value={NONE_FIELD_VALUE} selected={!group.subjectId}>Ikke valgt</option>
                  {#each subjectsForSelectedSchool as subject}
                    <option value={subject.id} selected={subject.id === group.subjectId}>
                      {subject.displayName}
                    </option>
                  {/each}
                </select>
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
            <ButtonIcon
              options={{
                iconName: 'alert-information',
                title: 'Toggle JSON',
                onClick: () => handleInfoToggle(group.id),
              }}
            />
          </div>
          {#if openRows[group.id]}
            <pre class="bg-info">{JSON.stringify(group, null, 2)}</pre>
          {/if}
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
    grid-template-columns: 2fr 2fr 1fr 0.5fr 0.3fr;
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
