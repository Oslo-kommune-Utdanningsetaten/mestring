<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import '@oslokommune/punkt-elements/dist/pkt-textinput.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import { urlStringFrom, fetchSubjectsForStudents } from '../utils/functions'
  import StudentRow from '../components/StudentRow.svelte'
  import { STUDENT_ROLE } from '../utils/constants'
  import { groupsList, usersList } from '../generated/sdk.gen'
  import type { GroupType, UserType, SubjectType } from '../generated/types.gen'

  const router = useTinyRouter()
  let selectedGroupId = $state<string | undefined>(undefined)
  let allGroups = $state<GroupType[]>([])
  let students = $state<UserType[]>([])
  let isLoadingGroups = $state<boolean>(false)
  let isLoadingStudents = $state<boolean>(false)
  let nameFilter = $state<string>('')
  let subjects = $state<SubjectType[]>([])

  let currentSchool = $derived($dataStore.currentSchool)
  let filteredStudents = $derived(
    nameFilter
      ? students.filter(
          student =>
            student.id === nameFilter ||
            student.name.toLowerCase().includes(nameFilter.toLowerCase())
        )
      : students
  )
  let selectedGroup = $derived<GroupType | undefined>(
    allGroups.find(group => group.id === selectedGroupId)
  )
  let headerText = $derived.by(() => {
    let text = selectedGroup ? `Elever i gruppe: ${selectedGroup.displayName}` : 'Alle elever'
    text = nameFilter ? `${text} med navn som inneholder "${nameFilter}"` : text
    return text
  })

  const fetchGroups = async () => {
    if (!currentSchool) return
    try {
      isLoadingGroups = true
      const result = await groupsList({
        query: {
          school: currentSchool?.id,
          isEnabled: true,
        },
      })
      allGroups = result.data || []
    } catch (error) {
      console.error('Error fetching groups:', error)
      allGroups = []
    } finally {
      isLoadingGroups = false
    }
  }

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
      await fetchSubjectsForStudents(students, $dataStore.subjects, currentSchool.id).then(
        fetchedSubjects => {
          subjects = fetchedSubjects
        }
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
      fetchGroups().then(() => {
        fetchStudents()
      })
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

<section class="pt-3">
  <h2 class="py-3">{headerText}</h2>
  <!-- Filter groups -->
  <div class="d-flex align-items-center gap-2">
    {#if isLoadingGroups}
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Henter data...</span>
      </div>
      <span>Henter grupper...</span>
    {:else}
      <div class="pkt-inputwrapper">
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
      <input type="text" class="filterStudentsByName" placeholder="Navn" bind:value={nameFilter} />
    {/if}
  </div>
</section>

<section class="py-3">
  {#if isLoadingStudents || isLoadingGroups}
    <div class="mt-3 spinner-border text-primary" role="status">
      <span class="visually-hidden">Henter data...</span>
    </div>
    <span>Henter data...</span>
  {:else if students.length === 0}
    <div class="mt-3">Her var det tomt, gitt.</div>
  {:else}
    <div class="students-grid" aria-label="Elevliste" style="--subject-count: {subjects.length}">
      <span class="item header header-row">Elev</span>
      {#each subjects as subject (subject.id)}
        <span class="item header header-row">
          <span class="subject-label-header">
            {subject.shortName}
          </span>
        </span>
      {/each}
      {#each filteredStudents as student (student.id)}
        <StudentRow {student} {subjects} groups={allGroups} />
      {/each}
    </div>
  {/if}
</section>

<style>
  .filterStudentsByName {
    border: 2px solid var(--bs-primary);
    border-radius: 0;
    height: 48px;
    margin-top: 0px;
    padding-left: 15px;
    margin-left: 10px;
  }

  .students-grid {
    display: grid;
    grid-template-columns: 2fr repeat(var(--subject-count, 8), 1fr);
    align-items: start;
    gap: 0;
  }

  .students-grid :global(.item) {
    padding: 0.5rem;
    border-top: 1px solid var(--bs-border-color);
    min-height: 4rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .students-grid :global(.item.header-row) {
    background-color: var(--bs-light);
    font-weight: 800;
  }

  .students-grid :global(.item.last-row) {
    border-bottom: 1px solid var(--bs-border-color);
  }

  .students-grid :global(.item.header:first-child),
  .students-grid :global(.item.student-name) {
    justify-content: flex-start;
  }

  .subject-label-header {
    transform: rotate(-60deg);
    font-size: 0.8rem;
  }
</style>
