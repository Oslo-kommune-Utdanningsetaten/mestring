<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import '@oslokommune/punkt-elements/dist/pkt-textinput.js'
  import '@oslokommune/punkt-elements/dist/pkt-tabs.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import type { GroupType, UserType, SubjectType } from '../generated/types.gen'
  import { subjectsList, usersList } from '../generated/sdk.gen'
  import { USER_ROLES, SUBJECTS_ALLOWED_CUSTOM } from '../utils/constants'
  import { dataStore } from '../stores/data'
  import { urlStringFrom, getGroupLabel } from '../utils/functions'
  import { preferredSchoolYear } from '../stores/localStorageFunctions'

  import StudentsWithSubjects from '../components/StudentsWithSubjects.svelte'
  import StudentsWithStatuses from '../components/StudentsWithStatuses.svelte'

  const router = useTinyRouter()

  let students = $state<UserType[]>([])
  let isLoadingStudents = $state<boolean>(false)
  let nameFilter = $state<string>('')
  let subjects = $state<SubjectType[]>([])

  const currentSchool = $derived($dataStore.currentSchool)
  const allGroups = $derived<GroupType[]>($dataStore.currentUser.allGroups || [])

  const focusOptions = $derived.by(() => {
    if (!$dataStore.statusCategories) return []
    const statusCategories: Record<string, any>[] = $dataStore.statusCategories
      .filter(cat => cat.isEnabled)
      .map(statusCategory => ({
        value: statusCategory.name,
        label: statusCategory.title,
      }))
    return statusCategories.concat([{ value: 'mastery', label: 'Mestring i fag' }])
  })

  const selectedGroupId = $derived(router.getQueryParam('group'))
  const selectedFocus = $derived(router.getQueryParam('focus') || focusOptions[0].value)

  const filteredStudents = $derived(
    nameFilter
      ? students.filter(
          student =>
            student.id === nameFilter ||
            student?.name?.toLowerCase().includes(nameFilter.toLowerCase())
        )
      : students
  )

  const selectedGroup = $derived<GroupType | undefined>(
    allGroups.find(group => group.id === selectedGroupId)
  )

  const headerText = $derived.by(() => {
    const result = ['Elever på skolen']
    if (selectedGroup) {
      result.push(
        `i ${getGroupLabel(selectedGroup, {
          isGroupNameEnabled: true,
          isGroupTypeNameEnabled: false,
          includeEarlierYear: true,
        })}`
      )
    }
    if (nameFilter) {
      result.push(`med navn som matcher "${nameFilter}"`)
    }
    return result.join(' ')
  })

  const fetchData = async () => {
    if (!currentSchool) return
    try {
      isLoadingStudents = true
      const studentQueryOptions = selectedGroupId
        ? { groups: selectedGroupId, school: currentSchool.id, roles: USER_ROLES.STUDENT }
        : { school: currentSchool.id, roles: USER_ROLES.STUDENT }
      const studentsResult = await usersList({
        query: studentQueryOptions,
      })
      students = studentsResult.data || []

      let localSubjects: SubjectType[] = []

      if (currentSchool.subjectsAllowed === SUBJECTS_ALLOWED_CUSTOM) {
        localSubjects = $dataStore.subjects
      } else {
        const subjectsResult = await subjectsList({
          query: {
            school: currentSchool.id,
            students: selectedGroupId ? students.map(s => s.id).join(',') : undefined,
            schoolYear: $preferredSchoolYear,
          },
        })
        localSubjects = subjectsResult.data || []
      }

      subjects = localSubjects.sort((a, b) => a.displayName.localeCompare(b.displayName))
    } catch (error) {
      console.error('Error fetching members', { selectedGroupId, error })
      students = []
      subjects = []
    } finally {
      isLoadingStudents = false
    }
  }

  const handleGroupSelect = (groupId: string): void => {
    const params: Record<string, string> = groupId === '0' ? {} : { group: groupId }
    if (selectedFocus) {
      params['focus'] = selectedFocus
    }
    router.navigate(urlStringFrom(params, { path: '/students', mode: 'replace' }))
  }

  const handleFocusSelect = (focusValue: string): void => {
    const params: Record<string, string> = { focus: focusValue }
    if (selectedGroupId) {
      params['group'] = selectedGroupId
    }
    router.navigate(urlStringFrom(params, { path: '/students', mode: 'replace' }))
  }

  // Redirect to the first focus option if none is selected
  $effect(() => {
    if (focusOptions.length > 1 && !router.getQueryParam('focus')) {
      const params: Record<string, string> = { focus: focusOptions[0].value }
      if (selectedGroupId) {
        params['group'] = selectedGroupId
      }
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
      <select
        class="pkt-input"
        id="groupSelect"
        onchange={(e: Event) => handleGroupSelect((e.target as HTMLSelectElement).value)}
      >
        <option value="0" selected={!selectedGroupId}>Hele skolen - ⚠️ kan ta lang tid</option>
        {#each allGroups as group}
          <option value={group.id} selected={group.id === selectedGroupId}>
            {getGroupLabel(group, {
              isGroupNameEnabled: true,
              isGroupTypeNameEnabled: false,
              includeEarlierYear: true,
            })}
          </option>
        {/each}
      </select>
    </div>

    <div class="filter-item">
      <!-- Filter by student name -->
      <label for="filterStudentsByName" class="mb-1 visually-hidden">Filtrer på navn:</label>
      <input
        type="text"
        id="filterStudentsByName"
        class="filterStudentsByName"
        placeholder="Navn"
        bind:value={nameFilter}
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
    <StudentsWithSubjects students={filteredStudents} {subjects} group={selectedGroup} />
  {:else if focusOptions.some(opt => opt.value === selectedFocus)}
    <StudentsWithStatuses
      students={filteredStudents}
      {subjects}
      categoryName={selectedFocus}
      group={selectedGroup}
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

  .filterStudentsByName {
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
