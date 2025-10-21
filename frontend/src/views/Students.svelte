<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import '@oslokommune/punkt-elements/dist/pkt-textinput.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import { urlStringFrom, fetchSubjectsForStudents } from '../utils/functions'
  import StudentRow from '../components/StudentRow.svelte'
  import { STUDENT_ROLE } from '../utils/constants'
  import { groupsList, usersList, goalsList } from '../generated/sdk.gen'
  import type { GroupType, GoalType, UserType, SubjectType } from '../generated/types.gen'

  const router = useTinyRouter()
  let currentSchool = $derived($dataStore.currentSchool)
  let selectedGroupId = $state<string | undefined>(undefined)
  let selectedGroup = $state<GroupType | undefined>(undefined)
  let allGroups = $state<GroupType[]>([])
  let students = $state<UserType[]>([])
  let nameFilter = $state<string>('')
  let filteredStudents = $derived(
    nameFilter
      ? students.filter(student => student.name.toLowerCase().includes(nameFilter.toLowerCase()))
      : students
  )
  let subjects = $state<SubjectType[]>([])
  let headerText = $derived.by(() => {
    let text = selectedGroup ? `Elever i gruppe: ${selectedGroup.displayName}` : 'Alle elever'
    text = nameFilter ? `${text} med navn som inneholder "${nameFilter}"` : text
    return text
  })
  let isLoadingGroups = $state<boolean>(false)
  let isLoadingStudents = $state<boolean>(false)
  let studentsGridElement = $state<HTMLElement | null>(null)

  const fetchAllStudentsInSchool = async () => {
    if (!currentSchool) return
    try {
      isLoadingStudents = true
      const studentsResult = await usersList({
        query: { roles: 'student', school: currentSchool.id },
      })
      students = studentsResult.data || []
    } catch (error) {
      console.error('Error fetching all students:', error)
      students = []
    } finally {
      isLoadingStudents = false
    }
  }

  const fetchAllGroups = async () => {
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

  const fetchGroupMembers = async (groupId: string) => {
    if (!currentSchool) return
    try {
      isLoadingStudents = true
      const studentsResult = await usersList({
        query: { groups: groupId, school: currentSchool.id, roles: STUDENT_ROLE },
      })
      students = studentsResult.data || []
    } catch (error) {
      console.error(`Error fetching members for group ${groupId}:`, error)
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
    if (students.length > 0) {
      fetchSubjectsForStudents(students, $dataStore.subjects, currentSchool.id).then(
        fetchedSubjects => {
          subjects = fetchedSubjects
        }
      )
    }
  })

  $effect(() => {
    currentSchool = $dataStore.currentSchool
  })

  $effect(() => {
    // Read selectedGroupId first to establish reactivity
    selectedGroupId = router.getQueryParam('groupId')
    if (currentSchool && currentSchool.id) {
      fetchAllGroups().then(() => {
        selectedGroup = allGroups.find(group => group.id === selectedGroupId)
        if (selectedGroup) {
          fetchGroupMembers(selectedGroup.id)
        } else {
          // fetch all students if no group is selected
          fetchAllStudentsInSchool()
        }
      })
    }
  })

  // Effect to apply last-row class to the last row of grid items
  $effect(() => {
    if (studentsGridElement && filteredStudents.length > 0 && subjects.length > 0) {
      // Remove existing last-row classes
      const allItems = studentsGridElement.querySelectorAll('.item')
      allItems.forEach(item => item.classList.remove('last-row'))

      // Calculate how many items are in the last row
      const totalColumns = subjects.length + 1 // +1 for student name column
      const totalItems = allItems.length
      const itemsInLastRow = totalColumns

      // Apply last-row class to the last row items
      for (let i = totalItems - itemsInLastRow; i < totalItems; i++) {
        if (allItems[i]) {
          allItems[i].classList.add('last-row')
        }
      }
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
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Henter data...</span>
    </div>
    <span>Henter data...</span>
  {:else if students.length > 0}
    <div
      bind:this={studentsGridElement}
      class="students-grid"
      aria-label="Elevliste"
      style="--subject-count: {subjects.length}"
    >
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
  {:else if !isLoadingStudents && !isLoadingGroups}
    <div class="alert alert-info">Ingen elever</div>
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
