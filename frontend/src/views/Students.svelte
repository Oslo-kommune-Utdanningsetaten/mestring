<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import '@oslokommune/punkt-elements/dist/pkt-textinput.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import StudentsWithSubjects from '../components/StudentsWithSubjects.svelte'
  import StudentsWithStatuses from '../components/StudentsWithStatuses.svelte'
  import { USER_ROLES } from '../utils/constants'
  import { subjectsList, usersList } from '../generated/sdk.gen'
  import type { GroupType, UserType, SubjectType } from '../generated/types.gen'

  const router = useTinyRouter()

  let students = $state<UserType[]>([])
  let isLoadingStudents = $state<boolean>(false)
  let nameFilter = $state<string>('')
  let subjects = $state<SubjectType[]>([])

  let currentSchool = $derived($dataStore.currentSchool)
  let allGroups = $derived<GroupType[]>($dataStore.currentUser.allGroups || [])

  const focusOptions = $derived.by(() => {
    if (!$dataStore.statusCategories) return []
    const options = [{ value: 'mastery', label: 'Mestring i fag' }]
    $dataStore.statusCategories
      .filter(cat => cat.isEnabled)
      .forEach(statusCategory => {
        options.push({ value: statusCategory.name, label: statusCategory.title })
      })
    return options
  })

  let selectedGroupId = $derived(router.getQueryParam('group'))
  let selectedFocus = $derived(router.getQueryParam('focus') || focusOptions[0].value)

  let filteredStudents = $derived(
    nameFilter
      ? students.filter(
          student =>
            student.id === nameFilter ||
            student?.name?.toLowerCase().includes(nameFilter.toLowerCase())
        )
      : students
  )

  let selectedGroup = $derived<GroupType | undefined>(
    allGroups.find(group => group.id === selectedGroupId)
  )
  let headerText = $derived.by(() => {
    const text = selectedGroup ? `Elever i gruppe: ${selectedGroup.displayName}` : 'Alle elever'
    return nameFilter ? `${text} med navn som inneholder "${nameFilter}"` : text
  })

  const fetchStudents = async () => {
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
      const subjectsResult = await subjectsList({
        query: { school: currentSchool.id, students: students.map(s => s.id).join(',') },
      })
      subjects = (subjectsResult.data || []).sort((a, b) =>
        a.displayName.localeCompare(b.displayName)
      )
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

  $effect(() => {
    if (currentSchool && currentSchool.id) {
      fetchStudents()
    }
  })
</script>

<section class="my-4">
  <h2 class="py-3">{headerText}</h2>
  <!-- Filter groups -->
  <div class="filters-container">
    <div class="filter-item">
      <!-- Filter by group membership -->
      <label for="groupSelect" class="mb-1 visually-hidden">Filtrer på gruppe:</label>
      <select
        class="pkt-input"
        id="groupSelect"
        onchange={(e: Event) => handleGroupSelect((e.target as HTMLSelectElement).value)}
      >
        <option value="0" selected={!selectedGroupId}>Velg gruppe</option>
        {#each allGroups as group}
          <option value={group.id} selected={group.id === selectedGroupId}>
            {group.displayName}
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

  {#if focusOptions.length > 1}
    <div class="d-flex flex-wrap gap-3 mt-3">
      <!-- Radio buttons for focus -->
      <fieldset class="border p-3 rounded">
        <legend class="fs-6 fw-bold">Fokus</legend>
        {#each focusOptions as option (option.value)}
          <label class="my-2 ms-1 d-block">
            <input
              type="radio"
              name="focusOptions"
              value={option.value}
              onclick={() => handleFocusSelect(option.value)}
              checked={selectedFocus === option.value}
            />
            <span class="ms-2">{option.label}</span>
          </label>
        {/each}
      </fieldset>
    </div>
  {/if}
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
  {:else if selectedFocus === focusOptions[0].value}
    <StudentsWithSubjects students={filteredStudents} {subjects} group={selectedGroup} />
  {:else if focusOptions.some(opt => opt.value === selectedFocus)}
    <StudentsWithStatuses students={filteredStudents} {subjects} category={selectedFocus} />
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
</style>
