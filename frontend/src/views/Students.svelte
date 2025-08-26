<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import '@oslokommune/punkt-elements/dist/pkt-textinput.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import StudentRow from '../components/StudentRow.svelte'
  import { STUDENT_ROLE } from '../utils/constants'
  import { groupsList, usersList, goalsList } from '../generated/sdk.gen'
  import type {
    GroupReadable,
    GoalReadable,
    UserReadable,
    SubjectReadable,
  } from '../generated/types.gen'

  const router = useTinyRouter()
  let currentSchool = $state($dataStore.currentSchool)
  let selectedGroupId = $state<string | undefined>(undefined)
  let selectedGroup = $state<GroupReadable | undefined>(undefined)
  let allGroups = $state<GroupReadable[]>([])
  let students = $state<UserReadable[]>([])
  let nameFilter = $state<string>('')
  let filteredStudents = $derived(
    nameFilter
      ? students.filter(student => student.name.toLowerCase().includes(nameFilter.toLowerCase()))
      : students
  )
  let subjects = $state<SubjectReadable[]>([])
  let headerText = $derived.by(() => {
    let text = selectedGroup ? `Elever i gruppe: ${selectedGroup.displayName}` : 'Alle elever'
    text = nameFilter ? `${text} med navn som inneholder "${nameFilter}"` : text
    return text
  })

  const fetchAllStudentsInSchool = async () => {
    if (!currentSchool) return
    try {
      const studentsResult = await usersList({
        query: { roles: 'student', school: currentSchool.id },
      })
      students = studentsResult.data || []
    } catch (error) {
      console.error('Error fetching all students:', error)
      students = []
    }
  }

  const fetchAllGroups = async () => {
    if (!currentSchool) return
    try {
      const result = await groupsList({
        query: {
          school: currentSchool?.id,
        },
      })
      allGroups = result.data || []
    } catch (error) {
      console.error('Error fetching groups:', error)
      allGroups = []
    }
  }

  const fetchGroupMembers = async (groupId: string) => {
    if (!currentSchool) return
    try {
      const studentsResult = await usersList({
        query: { groups: groupId, school: currentSchool.id, roles: STUDENT_ROLE },
      })
      students = studentsResult.data || []
    } catch (error) {
      console.error(`Error fetching members for group ${groupId}:`, error)
      students = []
    }
  }

  const fetchSubjectsForStudents = async (students: UserReadable[]) => {
    const subjectIds = new Set(subjects.map(s => s.id))

    const goalsArrays = await Promise.all(
      students.map(async (student): Promise<GoalReadable[]> => {
        const result = await goalsList({
          query: { student: student.id },
        })
        return Array.isArray(result.data) ? result.data : []
      })
    )

    const newSubjects: SubjectReadable[] = []
    goalsArrays.forEach(goals => {
      goals?.forEach(goal => {
        if (goal.subjectId && !subjectIds.has(goal.subjectId)) {
          const subject = $dataStore.subjects.find(s => s.id === goal.subjectId)
          if (subject) {
            newSubjects.push(subject)
            subjectIds.add(subject.id)
          }
        }
      })
    })

    if (newSubjects.length > 0) {
      subjects = [...subjects, ...newSubjects]
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
      fetchSubjectsForStudents(students)
    }
  })

  $effect(() => {
    currentSchool = $dataStore.currentSchool
  })

  $effect(() => {
    // Read both dependencies first to establish reactivity
    selectedGroupId = router.getQueryParam('groupId')
    if (!currentSchool) return
    fetchAllGroups().then(() => {
      selectedGroup = allGroups.find(group => group.id === selectedGroupId)
      if (selectedGroup) {
        fetchGroupMembers(selectedGroup.id)
      } else {
        // fetch all students if no group is selected
        fetchAllStudentsInSchool()
      }
    })
  })
</script>

<section class="pt-3">
  <h2 class="py-3">{headerText}</h2>
  <!-- Filter groups -->
  <div class="d-flex align-items-center gap-2">
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
  </div>
</section>

<section class="py-3">
  {#if students.length > 0}
    <div class="card shadow-sm">
      <!-- Header row -->
      <div class="student-grid-row fw-bold header">
        <div>Navn</div>
        <div class="group-grid-columns">
          {#each subjects as subject}
            <span>{subject.displayName}</span>
          {/each}
        </div>
      </div>

      <!-- Student rows -->
      {#each filteredStudents as student}
        <StudentRow {student} {subjects} />
      {/each}
    </div>
  {:else}
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
</style>
