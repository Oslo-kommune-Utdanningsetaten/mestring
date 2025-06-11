<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import '@oslokommune/punkt-elements/dist/pkt-textinput.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import StudentRow from './StudentRow.svelte'

  import {
    groupsList,
    groupsMembersRetrieve,
    usersGoalsRetrieve,
    schoolsUsersRetrieve,
  } from '../generated/sdk.gen'
  import {
    type GroupReadable,
    type GoalReadable,
    type NestedGroupUserReadable,
    type UserReadable,
    type SubjectReadable,
  } from '../generated/types.gen'

  const router = useTinyRouter()
  const currentSchool = $state($dataStore.currentSchool)

  let selectedGroupId = $derived(router.getQueryParam('groupId'))
  let selectedGroup = $state<GroupReadable | null>(null)
  let allGroups = $state<GroupReadable[]>([])
  let students = $state<UserReadable[]>([])
  let filteredStudents = $state<UserReadable[]>([])
  let subjects = $state<SubjectReadable[]>([])
  let nameFilter = $state<string>('')
  let headerText = $derived(
    selectedGroup ? `Elever i gruppe: ${selectedGroup.displayName}` : 'Alle elever'
  )

  async function fetchAllStudentsInSchool() {
    if (!currentSchool?.id) return

    try {
      const result = await schoolsUsersRetrieve({
        path: { id: currentSchool.id },
        query: { roles: 'student' },
      })
      students = Array.isArray(result.data) ? result.data : []
    } catch (error) {
      console.error('Error fetching all students:', error)
      students = []
    }
  }

  async function fetchAllGroups() {
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

  async function fetchGroupMembers(groupId: string) {
    try {
      const result = await groupsMembersRetrieve({
        path: {
          id: groupId,
        },
      })
      const members: any = result.data || []
      students =
        members
          .filter((member: NestedGroupUserReadable) => member.role.name === 'student')
          .map((member: NestedGroupUserReadable) => member.user) || []
    } catch (error) {
      console.error(`Error fetching members for group ${groupId}:`, error)
      students = []
    }
  }

  async function fetchSubjectsForStudents(students: UserReadable[]) {
    const goalsArrays = await Promise.all(
      students.map(async (student): Promise<GoalReadable[]> => {
        const result = await usersGoalsRetrieve({
          path: {
            id: student.id,
          },
        })
        return Array.isArray(result.data) ? result.data : []
      })
    )
    goalsArrays.forEach(goals => {
      if (goals) {
        goals.forEach(goal => {
          const subject = $dataStore.subjects.find(s => s.id === goal.subjectId)
          if (subject && !subjects.some(s => s.id === subject.id)) {
            subjects.push(subject)
          }
        })
      }
    })
  }

  function handleGroupSelect(groupId: string): void {
    if (groupId && groupId !== '0') {
      window.location.href = urlStringFrom({ groupId }, { mode: 'merge' })
    } else {
      window.location.href = urlStringFrom({}, { mode: 'replace' })
    }
  }

  $effect(() => {
    if (currentSchool) {
      fetchAllGroups().then(() => {
        if (selectedGroupId) {
          selectedGroup = allGroups.find(group => group.id === selectedGroupId) || null
          fetchGroupMembers(selectedGroupId)
        } else {
          // fetch all students if no group is selected
          fetchAllStudentsInSchool()
        }
      })
    }
  })

  $effect(() => {
    if (students.length > 0) {
      fetchSubjectsForStudents(students)
    }
  })

  $effect(() => {
    if (nameFilter) {
      filteredStudents = students.filter(student =>
        student.name.toLowerCase().includes(nameFilter.toLowerCase())
      )
    } else {
      filteredStudents = students
    }
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
