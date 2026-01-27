<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import '@oslokommune/punkt-elements/dist/pkt-textinput.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import StudentsWithSubjects from '../components/StudentsWithSubjects.svelte'
  import { STUDENT_ROLE } from '../utils/constants'
  import { subjectsList, usersList } from '../generated/sdk.gen'
  import type { GroupType, UserType, SubjectType } from '../generated/types.gen'

  const router = useTinyRouter()
  let selectedGroupId = $state<string | undefined>(undefined)
  let allGroups = $derived<GroupType[]>($dataStore.currentUser.allGroups || [])
  let students = $state<UserType[]>([])
  let isLoadingStudents = $state<boolean>(false)
  let nameFilter = $state<string>('')
  let subjects = $state<SubjectType[]>([])

  let currentSchool = $derived($dataStore.currentSchool)
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
      const queryOptions = selectedGroupId
        ? { groups: selectedGroupId, school: currentSchool.id, roles: STUDENT_ROLE }
        : { school: currentSchool.id, roles: STUDENT_ROLE }
      const studentsResult = await usersList({
        query: queryOptions,
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
    } finally {
      isLoadingStudents = false
    }
  }

  const handleGroupSelect = (groupId: string): void => {
    if (groupId && groupId !== '0') {
      router.navigate(urlStringFrom({ groupId }, { path: '/students', mode: 'merge' }))
    } else {
      router.navigate(urlStringFrom({}, { path: '/students', mode: 'replace' }))
    }
  }

  $effect(() => {
    if (currentSchool && currentSchool.id) {
      fetchStudents()
    }
  })

  $effect(() => {
    const newGroupId = router.getQueryParam('groupId')
    if (newGroupId !== selectedGroupId) {
      selectedGroupId = newGroupId
      fetchStudents()
    }
  })
</script>

<section class="my-4">
  <h2 class="py-3">{headerText}</h2>
  <!-- Filter groups -->
  <div class="filters-container">
    <div class="filter-item">
      <label for="groupSelect" class="mb-1">Filtrer på gruppe:</label>
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
      <label for="filterStudentsByName" class="mb-1">Filtrer på navn:</label>
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
    <div class="mt-3 spinner-border text-primary" role="status">
      <span class="visually-hidden">Henter data...</span>
    </div>
    <span>Henter data...</span>
  {:else if students.length === 0}
    <div class="mt-3">Her var det tomt, gitt.</div>
  {:else}
    <StudentsWithSubjects students={filteredStudents} {subjects} groups={allGroups} />
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
