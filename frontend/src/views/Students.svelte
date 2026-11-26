<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import '@oslokommune/punkt-elements/dist/pkt-textinput.js'
  import '@oslokommune/punkt-elements/dist/pkt-tabs.js'
  import { setPktStrings } from '@oslokommune/punkt-elements'
  import { useTinyRouter } from 'svelte-tiny-router'

  import type { GroupType, UserType, SubjectType } from '../generated/types.gen'
  import { subjectsList, usersList } from '../generated/sdk.gen'
  import {
    USER_ROLES,
    SUBJECTS_ALLOWED_CUSTOM,
    STATUS_CATEGORY_TITLE_BY_NAME,
  } from '../utils/constants'
  import { dataStore } from '../stores/data'
  import { urlStringFrom, getGroupLabel } from '../utils/functions'
  import { preferredSchoolYear } from '../stores/localStorageFunctions'

  import StudentsWithSubjects from '../components/StudentsWithSubjects.svelte'
  import StudentsWithStatuses from '../components/StudentsWithStatuses.svelte'

  const router = useTinyRouter()

  // Punkt component string overrides. Empty strings should hide the whole row.
  setPktStrings({
    listbox: { addValue: '', empty: 'Ingen grupper matcher dette navnet' },
    combobox: { noResults: '' },
  })

  let students = $state<UserType[]>([])
  let isLoadingStudents = $state<boolean>(false)
  let studentNameFilter = $state<string>('')
  let subjects = $state<SubjectType[]>([])

  const currentSchool = $derived($dataStore.currentSchool)
  const allGroups = $derived<GroupType[]>($dataStore.currentUser.allGroups || [])

  const groupComboboxOptions = $derived.by(() => {
    return allGroups.map(group => ({
      value: group.id,
      label: getGroupLabel(group, {
        isGroupNameEnabled: true,
        isGroupTypeNameEnabled: false,
        includeEarlierYear: true,
      }),
    }))
  })

  const focusOptions = $derived.by(() => {
    if (!$dataStore.statusCategories) return []
    const statusCategories: Record<string, any>[] = $dataStore.statusCategories
      .filter(cat => cat.isEnabled)
      .map(statusCategory => ({
        value: statusCategory.name,
        label: STATUS_CATEGORY_TITLE_BY_NAME[statusCategory.name],
      }))
    return statusCategories.concat([{ value: 'mastery', label: 'Mestring i fag' }])
  })

  //const selectedGroupIds = $derived(router.getQueryParam('groups')?.split(',') || [])
  let selectedGroupIds = $state<string[]>([])
  const selectedFocus = $derived(router.getQueryParam('focus') || focusOptions[0].value)

  const filteredStudents = $derived(
    studentNameFilter
      ? students.filter(
          student =>
            student.id === studentNameFilter ||
            student?.name?.toLowerCase().includes(studentNameFilter.toLowerCase())
        )
      : students
  )

  const selectedGroups = $derived.by(() => {
    const groups = allGroups.filter(group => selectedGroupIds.includes(group.id))
    return groups
  })

  const headerText = $derived.by(() => {
    const result = ['Elever']
    if (selectedGroups.length > 0) {
      result.push('i valgte grupper')
    } else {
      result.push('på skolen')
    }
    if (studentNameFilter) {
      result.push(`med navn som matcher "${studentNameFilter}"`)
    }
    return result.join(' ')
  })

  const fetchData = async () => {
    if (!currentSchool) return
    try {
      isLoadingStudents = true
      let query: { school: any; roles: USER_ROLES; groups?: string } = {
        school: currentSchool.id,
        roles: USER_ROLES.STUDENT,
      }
      if (selectedGroupIds.length > 0) {
        query.groups = selectedGroupIds.join(',')
      }
      const studentsResult = await usersList({ query })
      students = studentsResult.data || []

      let localSubjects: SubjectType[] = []

      if (currentSchool.subjectsAllowed === SUBJECTS_ALLOWED_CUSTOM) {
        localSubjects = $dataStore.subjects
      } else {
        const subjectsResult = await subjectsList({
          query: {
            school: currentSchool.id,
            students: selectedGroupIds.length > 0 ? students.map(s => s.id).join(',') : undefined,
            schoolYear: $preferredSchoolYear,
          },
        })
        localSubjects = subjectsResult.data || []
      }

      subjects = localSubjects.sort((a, b) => a.displayName.localeCompare(b.displayName))
    } catch (error) {
      console.error('Error fetching members', { selectedGroupIds, error })
      students = []
      subjects = []
    } finally {
      isLoadingStudents = false
    }
  }

  const handleSelectMatchingGroups = (matcher: string): void => {
    if (!matcher) return
    const localSelectedGroupIds = allGroups
      .filter(
        group =>
          group.id === matcher ||
          group.displayName.toLocaleLowerCase().includes(matcher.toLocaleLowerCase())
      )
      .map(group => group.id)

    selectedGroupIds = localSelectedGroupIds
  }

  const handleUpdateSelectedGroups = (commaSeparatedGroupIds: string) => {
    if (commaSeparatedGroupIds.trim() === '') return
    selectedGroupIds = commaSeparatedGroupIds.split(',')
  }

  const handleFocusSelect = (focusValue: string): void => {
    const params: Record<string, string> = { focus: focusValue }
    router.navigate(urlStringFrom(params, { path: '/students', mode: 'replace' }))
  }

  // Redirect to the first focus option if none is selected
  $effect(() => {
    if (focusOptions.length > 1 && !router.getQueryParam('focus')) {
      const params: Record<string, string> = { focus: focusOptions[0].value }
      router.navigate(urlStringFrom(params, { path: '/students', mode: 'replace' }))
    }
  })

  $effect(() => {
    if (currentSchool && currentSchool.id) {
      fetchData()
    }
  })
</script>

<section class="my-4">
  <h2>{headerText}</h2>

  <!-- Focus / view-mode switch if more than one option -->
  {#if focusOptions.length > 1}
    <div class="focus-row mt-3 mb-4">
      {#if focusOptions.length > 1}
        <pkt-tabs
          ontab-selected={(event: CustomEvent) =>
            handleFocusSelect(focusOptions[event.detail.index].value)}
        >
          {#each focusOptions as option, index (option.value)}
            <pkt-tab-item {index} active={selectedFocus === option.value}>
              {option.label}
            </pkt-tab-item>
          {/each}
        </pkt-tabs>
      {/if}
    </div>
  {/if}

  <!-- Filter groups -->
  <div class="filters-container mt-3">
    <div class="filter-item">
      <!-- Filter by group membership -->
      <label for="groupSelect" class="mb-1 visually-hidden">Filtrer på gruppe:</label>
      <pkt-combobox
        label=""
        placeholder={selectedGroupIds.length === 0
          ? 'Hele skolen - ⚠️ kan ta lang tid'
          : selectedGroupIds.length +
            ' guppe' +
            (selectedGroupIds.length === 1 ? '' : 'r') +
            ' valgt'}
        typeahead
        multiple
        fullwidth={true}
        tagPlacement="outside"
        value={selectedGroupIds.join(',')}
        onchange={(event: Event) => {
          const target = event.target as HTMLSelectElement
          handleUpdateSelectedGroups(target.value)
        }}
        onsearch={(event: CustomEvent) => handleSelectMatchingGroups(event.detail)}
        options={groupComboboxOptions}
      ></pkt-combobox>
    </div>
  </div>

  <!-- Filter students -->
  <div class="filters-container mt-3">
    <div class="filter-item">
      <!-- Filter by student name -->
      <label for="filterByName" class="mb-1 visually-hidden">Filtrer på elevnavn:</label>
      <input
        type="text"
        id="filterByName"
        class="filterByName"
        placeholder="Elevnavn inneholder"
        bind:value={studentNameFilter}
      />
    </div>
  </div>
</section>

<section class="my-4">
  {#if isLoadingStudents}
    <div class="d-flex align-items-center gap-2 text-secondary small py-2">
      <span
        class="spinner-border spinner-border-sm"
        role="status"
        aria-label="Henter elever"
      ></span>
      <span>Henter elever...</span>
    </div>
  {:else if students.length === 0}
    <div class="mt-3">Her var det tomt</div>
  {:else if selectedFocus === 'mastery'}
    <StudentsWithSubjects
      students={filteredStudents}
      {subjects}
      group={selectedGroups[0] ?? undefined}
    />
  {:else if focusOptions.some(opt => opt.value === selectedFocus)}
    <StudentsWithStatuses
      students={filteredStudents}
      {subjects}
      categoryName={selectedFocus}
      groups={selectedGroups ?? []}
    />
  {:else}
    <div class="mt-3">Ukjent fokusvalg: {selectedFocus}</div>
  {/if}
</section>

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

  .filterByName {
    border: 2px solid var(--bs-primary);
    border-radius: 0;
    height: 48px;
    margin-top: 0px;
    padding-left: 15px;
  }

  .focus-row :global(.pkt-tabs__list) {
    padding: 0;
  }

  .focus-row :global(.status-categories-link) {
    white-space: nowrap;
  }

  /* Suppress the lingering focus frame after a mouse click,
     but keep it for keyboard users (:focus-visible) for accessibility. */
  .focus-row :global(.pkt-tabs__link:focus:not(:focus-visible)),
  .focus-row :global(.pkt-tabs__button:focus:not(:focus-visible)) {
    outline: 0;
  }
</style>
